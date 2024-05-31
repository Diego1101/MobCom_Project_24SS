# Helper functions to generate routes with scripts from the sumo tool collection.

# @author  Steven Duong (WS21/22)
# @author  Daniel Kahrizi (WS21/22)
# @author  Andre Vaskevic (WS21/22)
# @author  Martin Dell (WS22/23)
# @date    18.11.2022

import contextlib
import os
import subprocess
from typing import Optional

import constants.paths as paths
import constants.traffic as traffic
from enums.VehicleType import VehicleType
from exceptions.sumo import UnconfiguredEnvironmentError
import generators.helper as helper
from generators.types import Trip


if paths.sumo_home not in os.environ:
    raise UnconfiguredEnvironmentError(f'Environment variable "{paths.sumo_home}" is not declared.')

# Path to SUMO random trip generator python script
SUMO_ROUTE_GENERATOR = os.path.join(os.environ[paths.sumo_home], 'tools', 'randomTrips.py')


class SumoRouteGenerator:
    """
    This class can be used to generate random demand with the help of RandomTripGenerator.py which is part of the official SUMO tools.
    The demand will be modelled by different manipulators such as a given vehicle distribution, a given time interval or amount of directional and random traffic

    Args:
        departure_start (int): global time setting when to depart the first vehicle. vehicles will be spread evenly between the start and end time
        departure_end (int): Like departureStartGlobal, only referenced to last vehicle
        repetition_rate (float): Repetition rate of the spreading event. e.g. time difference = 60-0 and repetition rate = 0.5 -> every 0.5seconds from 0..60sec a vehicle will be spawned
        net_filepath (str): Filepath to the *.net.xml. Needed for validation of trips.
        temp_dir (str): Temporary working directory to store files during generation.
        vehicle_type (VehicleType): Vehicle class used for the random trips
        trip_id_prefix (str): Prefix that can be put in front of id=prefixTripId... at xml string
        seed (int): Seed value to regenerate the same random trip to reproduce the same results
        min_trip_distance (int): Minimum travel distance of a single trip in meters
        fringe_factor (int): Increase value, that vehicle tend to spawn more likely at the border of the map
        despawn_rate_per_tick (int): Despawn rate per tick, amount = 1/rate
    """

    def __init__(self,
                 departure_start: int,
                 departure_end: int,
                 repetition_rate: float,
                 net_file_path: str,
                 temp_dir: str,
                 vehicle_type: VehicleType = VehicleType.PASSENGER,
                 trip_id_prefix: str = '',
                 seed: int = 3,
                 min_trip_distance: int = traffic.MIN_TRIP_DISTANCE,
                 fringe_factor: int = traffic.FRINGE_FACTOR,
                 despawn_rate_per_tick: int = traffic.DESPAWN_RATE):
        """
            Initialize the class with the following given parameters
        """
        self.departure_start = departure_start
        self.departure_end = departure_end
        self.repetition_rate = repetition_rate
        self.net_file_path = net_file_path
        self.temp_dir = temp_dir
        self.vehicle_type = vehicle_type
        self.trip_id_prefix = trip_id_prefix
        self.seed = seed
        self.min_trip_distance = min_trip_distance
        self.fringe_factor = fringe_factor
        self.despawn_rate_per_tick = despawn_rate_per_tick

        # Trip attributes for every trip
        self.trip_attributes = {
            'type': vehicle_type,
            **traffic.trip_attributes
            }

    def __call__(self):
        return self.generate()

    def generate(self) -> 'list[Trip]':
        """
        Generate random trips using the `randomTrips.py` from the sumo tool collection.

        Trips will be validated and checked if each vehicle can reach its target edge.
        Reaching its target edge is not always possible, e.g. due to missing vehicle permission on a particular edge.

        Returns:
            list[str]: List of trips
        """
        temp_trip_file = os.path.join(self.temp_dir, f'{self.vehicle_type}.xml')
        temp_route_file = os.path.join(self.temp_dir, f'{self.vehicle_type}.routes.rou.xml')
        temp_additional_file = os.path.join(self.temp_dir, f'{self.vehicle_type}_additional.xml')

        with contextlib.suppress(FileNotFoundError):
            os.remove(temp_trip_file)
            os.remove(temp_additional_file)

        self._create_additional_file(temp_additional_file, self.vehicle_type)

        trip_attributes = ' '.join(helper.toxmlattr(self.trip_attributes))
        vclass = traffic.get_vclass(self.vehicle_type)

        cmd = [
            'python',
            SUMO_ROUTE_GENERATOR,
            '-n', self.net_file_path,
            '-o', temp_trip_file,
            '-r', temp_route_file,
            '-b', str(self.departure_start),
            '-e', str(self.departure_end),
            '-p', str(self.repetition_rate),
            '--additional-file', temp_additional_file,
            '--min-distance', str(self.min_trip_distance),
            '--seed', str(self.seed),
            '--fringe-factor', str(self.fringe_factor),
            '--edge-permission', vclass,
            '--trip-attributes', trip_attributes,
            '--remove-loops',
            '--validate',
        ]

        try:
            subprocess.run(cmd, timeout=traffic.TRIP_GENERATION_TIMEOUT, check=True)
        except Exception as e:
            raise Exception('Failed to generate random trips with SUMO script.') from e

        trips = helper.parse_trips(temp_trip_file, self.trip_id_prefix)

        # Clean up after generation
        with contextlib.suppress(FileNotFoundError):
            os.remove(temp_trip_file)
            os.remove(temp_additional_file)

        return trips

    def _create_additional_file(self, file: str, vehicle_type: VehicleType):
        """
        Creates an additional file containing definitions needed by SUMO.
        In this case the custom vtypes are written to this file.

        Args:
            file (str): File to write the additional information for SUMO.
            vehicle_type (VehicleType): Vehicle type for which to write the custom vtype for.
        """
        lines: list[str] = [
            '<additional>\n\t',
            helper.generate_vtype(vehicle_type),
            '\n</additional>',
            ]

        with open(file, 'w') as f:
            f.writelines(lines)


def clean_invalid_trips(route_file: str, output_file: str, net_file_path: str,
                        seed: int = 3, log_file: Optional[str] = None):
    """
    Validate trips of a route XML file with `duarouter` and save valid trips to output file.

    Args:
        route_file (str): Path to the input trips file that will be validated by `duarouter`
        output_file (str): Path where to save the valid trips of the input file.
        net_file_path (str): Path to the SUMO-net-file (*.net.xml) that will be used by `duarouter` to validate the trips.
        seed (int): Seed for random number generators.
        log_file (str): Path to log file. Default is no log file.
    """
    print('\nCleaning invalid trips...')

    log_args = ['--log', log_file] if log_file else []

    # Example call: duarouter -n osm.net.xml -t eveningDemand.rou.xml -o eveningDemand_val.rou.xml --write-trips --remove-loops --route-steps 1000000 --log dualog
    try:
        subprocess.run(['duarouter',
                        '-n', net_file_path,
                        '--route-files', route_file,
                        '-o', output_file,
                        '--write-trips',
                        '--remove-loops',
                        '--route-steps', '1000000',
                        '--seed', str(seed)]
                       + log_args)
    except Exception as e:
        raise Exception('Could not clean invalid trips.') from e

    print('Done cleaning trips.')
