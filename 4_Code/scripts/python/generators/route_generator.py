# This file contains the main route generator used to create random trips for vehicles
# in the simulation.

# @author  Andre Vaskevic (WS21/22)
# @author  Martin Dell (WS22/23)
# @date    18.11.2022


import math
import random
from typing import Optional

import constants.traffic as traffic
import generators.helper as helper
import utils.PathUtil as PathUtil
from enums.FileType import FileType
from enums.FolderType import FolderType
from enums.StrategyType import StrategyType
from enums.VehicleType import VehicleType
from exceptions.sumo import NoTripsError, TripNotFoundError
from generators.sumo_generator import SumoRouteGenerator
from generators.types import Trip
from joblib import Parallel, delayed
from utils.configuration import SimConfig


class DemandGenerator:
    """
    This class can be used to generate a SUMO demand *.xml-file (*.trips.xml).
    The demand will be modelled by different manipulators such as a given vehicle distribution, a given time interval or amount of directional and random traffic

    Args:
        spawn_start_time (int): The first trip will start at given value.
        spawn_end_time (int): The last trip will start at given value. Trips will be evenly distributed from start to end
        vehicle_type_distribution (dict[VehicleType, float]): Each float mapped to a vehicle class is a factor for the amount of total trips for the given class.
        spawn_edges (list[str]): Manual trips are defined by spawning edges and goal edges. This array of edges (str) define the spawn points for the manual trips.
        spawn_distribution (list[float]): Must be of the same length as spawn_edges. Each double corresponds to the spawn_edge (same index)
                                                and represents a factor by which the amount of trips for the corresponding spawn edge will be manipulated.
                                                E.g. 2 edges, first has a factor of 0.3 and the second edge has 0.7 -> 30% of trips will spawn at edge 1
                                                70% will spawn at edge two.
        goal_edges (list[str]): Array of strings. Each string represents a goal edge. Goal edges will be evenly distributed over all trips.
        prefix (str): This ID-Prefix will be put before each manual trip: <trip id=\"{self.prefix}{self.id} ..."
        additional_trips (list[Trip]): Additional custom trips which should also be added to the total trip list.
    """

    def __init__(self,
                 cfg: SimConfig,
                 spawn_start_time: float,
                 spawn_end_time: float,
                 vehicle_type_distribution: 'dict[VehicleType, float]',
                 additional_trips: 'list[Trip]' = [],
                 trip_id_prefix: str = 'Rand_'):

        self.cfg = cfg
        self.spawn_start_time = spawn_start_time
        self.spawn_end_time = spawn_end_time
        self.vehicle_type_distribution = helper.normalize_vehicle_distribution(vehicle_type_distribution)
        self.trip_id_prefix = trip_id_prefix

        self.additional_trips = additional_trips

        if self.cfg.spawn_rate <= 0:
            raise ValueError('Spawn delay cannot be zero or negative.')

        self.n_vehicles = math.floor(self.cfg.sim_time * self.cfg.spawn_rate / 60)  # Spawn rate min -> sec
        self.vehicle_type_amounts = self.get_vehicle_amounts(self.n_vehicles, self.vehicle_type_distribution)

        self.net_filepath = PathUtil.get_path(FileType.NET, self.cfg, must_exist=True)
        print('Network file:', self.net_filepath)

    def get_vehicle_amounts(self, n_vehicles: int, distribution: 'dict[VehicleType, float]') -> 'dict[VehicleType, int]':
        """Distributes the total amount of vehicles (n_vehicles) across all vehicles types.

        Args:
            n_vehicles (int): Total number of vehicles.
            distribution (dict[VehicleType, float]): Percentages of vehicles types.

        Returns:
            dict[VehicleType, int]: Amount of vehicles per type.
        """

        amounts = {veh_type: math.floor(n_vehicles * dist) for (veh_type, dist) in distribution.items()}

        # Distribute the missing amount of vehicles over all types uniformly
        all_types = list(amounts.keys())
        n_vehicles_missing = n_vehicles - sum(amounts.values())
        for i in range(n_vehicles_missing):
            amounts[all_types[i % len(all_types)]] += 1

        # Remove all vehicles types where amount is 0
        amounts = {veh_type: amount for (veh_type, amount) in amounts.items() if amount > 0}

        return amounts

    def generate_random_trips(self) -> 'list[Trip]':
        """Generates random trips for each vehicle class given via vehicle_type_distribution.

        Returns:
            list[Trip]: List of random trips with given type distribution.
        """
        temp_dir = PathUtil.makedir(FolderType.TEMP, self.cfg)
        print('Temporary working directory:', temp_dir)

        random_state = random.getstate()

        # Generate random route for each vehicle type in parallel
        # Because this tasks is redirected to a SUMO helper script, this will speed up generation of routes immensely
        with Parallel(n_jobs=self.cfg.n_jobs, verbose=5) as parallel:
            results: list[list[Trip]] = parallel(delayed(generate_random_trip)(
                vehicle_type,
                n_vehicles,
                self.spawn_start_time,
                self.spawn_end_time,
                temp_dir,
                self.net_filepath,
                self.trip_id_prefix,
                self.cfg.seed * (1 + i)  # Different seed for each vehicle type so that the edges have more variety
                ) for i, (vehicle_type, n_vehicles) in enumerate(self.vehicle_type_amounts.items()))  # type: ignore

            # Flatten list
            trips = [item for sublist in results for item in sublist]

        # Reset random state after trip generation
        # (generate_random_trip reseeds the random generator)
        random.setstate(random_state)

        return trips

    def __call__(self):
        return self.generate()

    def generate(self) -> 'list[Trip]':
        """
        Generates trips/routes for current simulation as configured.

        Depending on the configuration these trips include random trips (spawn/goal on the given net)
        and additional custom trips (e.g. an emergency vehicle).

        Returns:
            list[Trip]: List of random generated, additional and attacker trips sorted by departure time.
        """
        print('Generating demand...')

        trips: list[Trip] = []

        if self.cfg.spawn_rate > 0:
            trips += self.generate_random_trips()

            print(f'Generated a total of {len(trips)} random trips (should: {self.n_vehicles}).')

        # Add additional custom trips
        if len(self.additional_trips) > 0:
            trips += self.additional_trips
            print(f'Added {len(self.additional_trips)} custom trips.')

        if self.cfg.attacker.strategy != StrategyType.ATTACKER_SERVICE:
            # Sort trips (random, manual and additional) by departure time
            return sorted(trips, key=lambda trip: trip.depart_time)

        # Add attacker if configured
        if not self.cfg.attacker.attacker_id:
            # Spawn attacker automatically
            attacker_trip, target_id = self.generate_attacker_trip(trips)

            self.cfg.attacker.attacker_id = attacker_trip.id
            self.cfg.attacker.target_id = target_id
            trips.append(attacker_trip)

            print(f'\nAdded attacker which spawns {self.cfg.attacker.spawn_delay}s behind target \"{target_id}\".')

        elif not self.trip_exists(trips, self.cfg.attacker.attacker_id):
            # Attacker id was specified but trip was not found
            raise TripNotFoundError(f'Attacker trip with id {self.cfg.attacker.attacker_id} does not exist.',
                                    trip_id=self.cfg.attacker.attacker_id)

        elif not self.trip_exists(trips, self.cfg.attacker.target_id):
            raise TripNotFoundError(f'Target trip with id {self.cfg.attacker.target_id} does not exist.',
                                    trip_id=self.cfg.attacker.target_id)

        # else attacker id and target id were configured correctly

        # Sort trips (random, manual and additional) by departure time
        return sorted(trips, key=lambda trip: trip.depart_time)

    def trip_exists(self, trips: 'list[Trip]', trip_id: Optional[str]) -> bool:
        """Checks if the trip with given id exists.

        Args:
            trips (list[Trip]): All generated trips.
            target_id (Optional[str]): Id of the trip so search for.

        Returns:
            bool: Trip exists.
        """
        if not trip_id:
            return False

        target_trip = self.get_target_trip(trips, trip_id)
        return target_trip is not None

    def get_target_trip(self, trips: 'list[Trip]', target_id: Optional[str]) -> 'Optional[Trip]':
        """Returns the trip of given target.

        Args:
            trips (list[Trip]): All generated trips.
            target_id (Optional[str]): Id of the target so search for.

        Returns:
            Optional[Trip]: Trip of the target or None if it does not exist.
        """
        if not target_id:
            return None

        return next((trip for trip in trips if trip.id == target_id), None)

    def generate_attacker_trip(self, trips: 'list[Trip]') -> 'tuple[Trip, str]':
        """
        Generate a trip for an attacker following either
        the target chosen in the configuration or a random one.

        Args:
            trips (list[Trip]): All generated trips so far. This list should include the targets trip.

        Raises:
            NoTripsError: `trips` list is empty.
            TargetNotFoundError: Target id chosen in the config does not exist.

        Returns:
            tuple[Trip, str]: Trip of the attacker and the target id he will follow.
        """
        if len(trips) == 0:
            raise NoTripsError('No trips and therefore not target to follow found.')

        if self.cfg.attacker.target_id:
            # Search for target in trips list
            target_trip = self.get_target_trip(trips, self.cfg.attacker.target_id)

            if target_trip is None:
                raise TripNotFoundError(f'Target trip with id {self.cfg.attacker.target_id} does not exist.',
                                        trip_id=self.cfg.attacker.target_id)
        else:
            # Choose target randomly
            # We don't want targets that spawn late in the simulation,
            # so we only pick from the first half of all trips that are sorted by departure time.

            # May be not efficient to sort trips once here and after adding attacker trip.
            # Attacker could be added with bisect lib from python.
            sorted_trips = sorted(trips, key=lambda trip: trip.depart_time)

            rand_idx = random.randint(0, len(sorted_trips) // 2)
            target_trip = sorted_trips[rand_idx]

        # TODO: We may want to pick a random goal edge so we show that our attacker actually
        # follows the target and not just drives its preprogrammed route.
        # The problem with this is that we assume that all edges are valid.
        # But this must not always be the case. The worst case is that this trip is
        # removed after the validation step by SUMO.

        rand_trip = random.choice(trips)
        rand_to_edge = rand_trip.to_edge

        kwargs = {
            **traffic.attacker,
            'depart_time': target_trip.depart_time + self.cfg.attacker.spawn_delay,
            'depart_lane': target_trip.depart_lane,
            'depart_speed': target_trip.depart_speed,
            'from_edge': target_trip.from_edge,
            'to_edge': rand_to_edge,
            }

        return Trip(**kwargs), target_trip.id


def generate_routes(cfg: SimConfig):
    """
    Create random traffic routes for SUMO.
    Created routes are stored in two files in the simulation scenario folder.

    Args:
        cfg (SimConfig): Simulation config.
    """

    generator = DemandGenerator(
        cfg,
        spawn_start_time=0,
        spawn_end_time=cfg.sim_time,
        vehicle_type_distribution=traffic.vehicle_type_distribution)

    sorted_trips = generator.generate()

    if not sorted_trips:
        raise NoTripsError('No trips generated.')
    else:
        print('Total number of trips (including custom and attacker):', len(sorted_trips))

    trips_outfile = PathUtil.get_path(FileType.ROUTE, cfg, must_exist=False)
    trips_writer = helper.TripXmlWriter(trips_outfile, traffic.vehicle_type_distribution.keys())

    trips_writer.write(sorted_trips)
    print('\nTrips written to:', trips_outfile)

    helper.remove_temp_files(cfg)


def generate_random_trip(
        vehicle_type: VehicleType,
        n_trips: int,
        spawn_start_time: int,
        spawn_end_time: int,
        temp_dir: str,
        net_filepath: str,
        trip_id_prefix: str,
        seed: int) -> 'list[Trip]':
    """Generate random trips for one vehicle type.

    Args:
        vehicle_type (VehicleType): The vehicle class to generate the trips for.
        n_trips (int): Amount of trips for given vehicle class.
        spawn_start_time (int): Spawn start time.
        spawn_end_time (int): Spawn end time.
        temp_dir (str): Path to a temporary working directory.
        net_filepath (str): SUMO network file.
        trip_id_prefix (str): Prefix of every trip id.
                              The vehicle type will be appended to this prefix
                              to create final trip id prefix.
        seed (int): Seed for random number generators.

    Returns:
        list[Trip]: Trips for given vehicle class.
    """
    if n_trips <= 0:
        return []

    # Reseed with new seed
    random.seed(seed)

    print(f'Generating {n_trips} random trips for vehicle type {vehicle_type} using seed {seed}...')

    # Add x% more routes because some may be deleted due to e.g. invalid edges.
    n_trips_total = math.ceil(n_trips * (1 + traffic.EXTRA_TRIP_BUFFER))
    repetition_rate = round((spawn_end_time - spawn_start_time) / n_trips_total, 4)

    generator = SumoRouteGenerator(spawn_start_time,
                                   spawn_end_time,
                                   repetition_rate=repetition_rate,
                                   net_file_path=net_filepath,
                                   temp_dir=temp_dir,
                                   vehicle_type=vehicle_type,
                                   trip_id_prefix=trip_id_prefix + str(vehicle_type),
                                   seed=seed)

    # Generate routes
    trips = generator()

    print(f'Generated {len(trips)} trips for vehicle type {vehicle_type}.')

    # When we are some trips short, just deal with it
    if (len(trips) - n_trips) <= 0:
        return trips

    # Remove extra trips randomly and return exactly n_trips number of trips
    return random.sample(trips, n_trips)
