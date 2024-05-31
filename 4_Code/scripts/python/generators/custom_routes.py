# This file contains classes which can be used to generate custom routes.
# This feature is work in process because it is not necessary to run the simulation
# (leftover of previous group, but modified to theoretically work with the improved framework).

# @author  Andre Vaskevic (WS21/22)
# @author  Martin Dell (WS22/23)
# @date    21.11.2022

import contextlib
import math
import os
import random
from enums.FolderType import FolderType

import generators.helper as helper
from generators.sumo_generator import clean_invalid_trips
import utils.PathUtil as PathUtil
from enums.FileType import FileType
from enums.LogFileType import LogFileType
from enums.VehicleType import VehicleType
from generators.types import Trip
from utils.configuration import SimConfig


class TripBundleGenerator:
    """
    Simple class that generates multiple trips.

    The demand will be modelled by different manipulators such as a given vehicle distribution, a given time interval or amount of directional and random traffic.
    The demand will be modelled when the constructor is called and can be obtained as string via method tostring()

    Args:
        spawn_edges (list[str]): Manual trips are defined by spawning edges and goal edges. This array of edges (string) define the spawn points for the manual trips.
        goal_edges (list[str]): Array of strings. Each string represents a goal edge. Goal edges will be evenly distributed over all trips.
        spawn_distribution (list[float]): Must be of the same length as spawn_edges. Each double corresponds to the spawn_edge (same index)
                                            and represents a factor by which the amount of trips for the corresponding spawn edge will be manipulated.
                                            E.g. 2 edges, first has a factor of 0.3 and the second edge has 0.7 -> 30% of trips will spawn at edge 1 70% will spawn at edge two.
        type_distribution (dict[VehicleType, float]): Each string represents a vehicle class, each corresponding double is a factor for the amount of total trips for the given class.
        spawn_start_time (float): The first trip will start at given value.
        spawn_end_time (float): The last trip will start at given value. Trips will be evenly distributed from start to end
        amount_trips (int): Specifies the amount of "manual" trips that will be generated.
        id_start (int): SUMO trip id starting value. Total SUMO ID will be <prefix><id_start>
        depart_lane (str): This can be "best" or the lane number of the spawn edge (e.g. 0)
        prefix (str): This ID-Prefix will be put before each manual trip: <trip id=\"{self.prefix}{self.id} ..."
    """

    def __init__(self,
                 spawn_edges: 'list[str]',
                 goal_edges: 'list[str]',
                 spawn_edge_distribution: 'list[float]',
                 type_distribution: 'dict[VehicleType, float]',
                 spawn_time_start: float,
                 spawn_time_end: float,
                 amount_trips: int,
                 id_start: int = 0,
                 depart_lane: str = 'best',
                 depart_speed: str = 'max',
                 prefix: str = ''):

        self.spawn_edges = spawn_edges
        self.goal_edges = goal_edges
        self.spawn_edge_distribution = spawn_edge_distribution
        self.type_distribution = type_distribution
        self.spawn_time_start = spawn_time_start
        self.spawn_time_end = spawn_time_end
        self.amount_trips = amount_trips
        self.id_start = id_start
        self.depart_lane = depart_lane
        self.depart_speed = depart_speed
        self.prefix = prefix

    def generate_trips(self) -> 'list[Trip]':
        """Generates trips as configured.

        Returns:
            list[Trip]: List of custom trips.
        """

        if self.amount_trips == 0:
            return []

        type_strings = self.generate_types()
        spawn_list = self.generate_spawns()
        goal_list = self.generate_goals()
        time_step = (self.spawn_time_end - self.spawn_time_start) * len(self.spawn_edges) / self.amount_trips
        spawn_time = self.spawn_time_start

        trips: list[Trip] = []

        for count, type in enumerate(type_strings):
            trip_id = f'{self.prefix}{self.id_start + count}'

            with contextlib.suppress(IndexError):
                trips.append(
                    Trip(id=trip_id,
                         type=type,
                         depart_time=spawn_time,
                         depart_lane=self.depart_lane,
                         depart_speed=self.depart_speed,
                         from_edge=spawn_list.pop(0),
                         to_edge=goal_list.pop(0)))

            if count % len(self.spawn_edges) == 0:
                spawn_time += time_step

        return trips

    def generate_types(self) -> 'list[VehicleType]':
        """Generates a certain amount of type-strings as given by type_distribution and amount_trips.

        Returns:
            list[VehicleType]: List of type strings. Length is amount_trips. Each element of this list is a vehicle type string.
                               e.g. this list contains 3x"passenger", 5x"truck", 10x"bicycle" in random order
                               the amount of each vehicle type is given by type_distribution * amount_trips.
        """
        types: list[VehicleType] = []

        for (veh_class, dist) in self.type_distribution.items():
            amount_trips_by_type = math.ceil(self.amount_trips * dist)
            print(f'Trips by type [{veh_class}]:', amount_trips_by_type)
            types += [veh_class] * amount_trips_by_type

        return types

    def generate_spawns(self) -> 'list[str]':
        """Generates a certain amount of spawn-strings as given by spawn_distribution and amount_trips.

        Returns:
            list[str]: List of spawning-edge strings. Length is amount_trips.
                       e.g. this list contains 2x"123456#1", 6x"456789#1", 10x"-123324#1" in random order
                       The amount of resulting edge-occurrences for each edge is given by spawn_distribution * amount_trips
        """
        spawns: list[str] = []

        for edge_idx, spawn_factor in enumerate(self.spawn_edge_distribution):
            amount_trips_per_spawn = math.ceil(spawn_factor * self.amount_trips)
            spawns += [self.spawn_edges[edge_idx]] * amount_trips_per_spawn

        random.shuffle(spawns)

        return spawns

    def generate_goals(self) -> 'list[str]':
        """Generates goal-strings (amount=amount_trips) with an equal distribution of goal-edges.

        Returns:
            list[str]: List of goal-edge strings. Length is amount_trips.
                       e.g. this list contains 3x"123456#1", 3x"456789#1", 3x"-123324#1" in random order
                       The amount of resulting edge-occurrences for each edge is given by amount_trips/len(goal_edges)
        """

        goals: list[str] = []
        for edge in self.goal_edges:
            goals += [edge] * math.ceil(self.amount_trips / len(self.spawn_edges))

        random.shuffle(goals)

        return goals


class CustomRouteGenerator:
    """
    This class can be used to generate custom trips.

    Args:
        cfg (SimConfig): Simulation configuration.
        spawn_start_time (int): The first trip will start at given value.
        spawn_end_time (int): The last trip will start at given value. Trips will be evenly distributed from start to end
        n_trips (int): Number of trips to generate.
        spawn_edges (list[str]): Manual trips are defined by spawning edges and goal edges. This array of edges (str) define the spawn points for the manual trips.
        goal_edges (list[str]): Array of strings. Each string represents a goal edge. Goal edges will be evenly distributed over all trips.
        spawn_edge_distribution (list[float]): Must be of the same length as spawn_edges. Each double corresponds to the spawn_edge (same index)
                                                and represents a factor by which the amount of trips for the corresponding spawn edge will be manipulated.
                                                E.g. 2 edges, first has a factor of 0.3 and the second edge has 0.7 -> 30% of trips will spawn at edge 1
                                                70% will spawn at edge two.
        vehicle_type_distribution (dict[VehicleType, float]): Each float mapped to a vehicle class is a factor for the amount of total trips for the given class.
        prefix (str): This ID-Prefix will be put before each manual trip: <trip id=\"{self.prefix}{self.id} ..."
        id_counter_start (int): SUMO trip id starting value. Total SUMO ID will be <prefix><id_start>
    """
    def __init__(self,
                 cfg: SimConfig,
                 spawn_start_time: float,
                 spawn_end_time: float,
                 n_trips: int,
                 spawn_edges: 'list[str]',
                 goal_edges: 'list[str]',
                 spawn_edge_distribution: 'list[float]',
                 vehicle_type_distribution: 'dict[VehicleType, float]',
                 prefix: str = 'ManVeh',
                 id_counter_start: int = 0):

        self.cfg = cfg
        self.spawn_start_time = spawn_start_time
        self.spawn_end_time = spawn_end_time

        if n_trips <= 0:
            raise ValueError('Number of custom trips need to be greater 0!')
        self.n_trips = n_trips

        if not self.spawn_edges:
            raise ValueError('No spawn edges defined!')

        self.spawn_edges = spawn_edges
        self.goal_edges = goal_edges

        self.spawn_edge_distribution = helper.normalize_spawn_distribution(spawn_edge_distribution)
        self.vehicle_type_distribution = helper.normalize_vehicle_distribution(vehicle_type_distribution)
        self.id_counter_start = id_counter_start
        self.prefix = prefix

        self.net_filepath = PathUtil.get_path(FileType.NET, self.cfg, must_exist=True)

        self.temp_dir = PathUtil.makedir(FolderType.TEMP, self.cfg)
        self.temp_trip_file = os.path.join(self.temp_dir, 'custom_routes.xml.tmp')

    def __call__(self):
        return self.generate()

    def generate(self) -> 'list[Trip]':
        """Generate the custom trips.

        Returns:
            list[Trip]: Created trips.
        """
        generator = TripBundleGenerator(self.spawn_edges,
                                        self.goal_edges,
                                        self.spawn_edge_distribution,
                                        self.vehicle_type_distribution,
                                        self.spawn_start_time,
                                        self.spawn_end_time,
                                        self.n_trips,
                                        id_start=self.id_counter_start,
                                        prefix=self.prefix)

        trips = generator.generate_trips()

        self.trips_writer = helper.TripXmlWriter(self.temp_trip_file, self.vehicle_type_distribution.keys())
        self.trips_writer.write(trips)

        # At this point the trips-xml is finished. However, the trips were not checked for validity.
        # E.g. when 10% of trips are bicycles and one spawn point given via spawn_points is an Autobahn
        # then 10% (assuming equal spawn distribution) of vehicles on that Autobahn will be bicycles.
        # SUMO will spawn this vehicle but will throw an error, since bicycles are on the disallow list on that edge.
        # Depending on the teleport time this will result in a traffic jam, since the bicycle has no route but was already spawned.

        # The solution is to use the duarouter to delete all trips that could not be verified and
        # save a second trips file that contains only valid trips.

        log_file = PathUtil.get_log(LogFileType.DUAROUTER, self.cfg) if not self.cfg.no_logging else None
        validated_trips_file = PathUtil.get_path(FileType.VALIDATED_ROUTE, self.cfg, must_exist=False)

        clean_invalid_trips(self.temp_trip_file, validated_trips_file, self.net_filepath, seed=self.cfg.seed, log_file=log_file)

        valid_trips = helper.parse_trips(validated_trips_file, self.prefix)
        print(f'Valid trips remaining: {len(valid_trips)} (removed: {len(trips) - len(valid_trips)}).')

        return valid_trips
