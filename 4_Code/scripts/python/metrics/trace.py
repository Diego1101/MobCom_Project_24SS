# This file reconstructs vehicle routes from received CAM messages.

# @author  Daniela Hörl (WS21/22)
# @author  Simon Seefeldt (WS22/23)
# @author  Martin Dell (WS22/23)
# @date    29.12.2022

from __future__ import annotations
from typing import Optional
import numpy as np
from metrics.types import Position, VehicleTrace, ReconstructedTrace, OriginalTrace
from metrics.utilities import CAM

EARTH_RADIUS = 6371  # Approx. radius of earth in km
POS_ERR_TOLERANCE = 0.003  # Max error from position estimation to target in km
HEADING_TOLERANCE = np.pi * 3 / 5  # Max tolerance in heading variation between two timestamps in radians


# Class for estimated routes
class VehicleDynamicId():
    def __init__(self, cam: CAM):
        self.pseudo_id = [cam.pseudo_id]  # Pseudo ID
        self.static_id = cam.static_id # Static vehicle ID
        self.width = cam.width  # Vehicle Width
        self.length = cam.length  # Vehicle Length
        self.longitude = [cam.longitude]  # Position Longitudinal in Microdegree
        self.latitude = [cam.latitude]  # Position Lateral in Microdegree
        self.speed = [cam.speed]  # Speed in cm/s
        self.heading = [cam.heading]  # Heading in degree
        self.timestamps = [cam.timestamp]  # Timestamps in s
        self.duration = 0  # Duration of tracing the route

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(sid={self.static_id}; pids={self.pseudo_id}; t_max={self.duration})'

    def __repr__(self) -> str:
        return self.__str__()

    # Comparison of ID
    def compare_id(self, new_id: int) -> bool:
        return self.pseudo_id[-1] == new_id

    # Comparison of width and length
    def compare_parameters(self, length_new: int, width_new: int) -> bool:
        return (length_new == self.length and width_new == self.width)

    def compute_new_lat(self, latitude: float, dy: float) -> float:
        """Computes the new latitude with given distance traveled.

        Args:
            latitude (float): last known latitude position
            dy (float): distance traveled in latitude direction

        Returns:
            float: New latitude position
        """
        return latitude + (dy / EARTH_RADIUS) * (180 / np.pi)

    def compute_new_long(self, longitude: float, latitude: float, dx: float) -> float:
        """Computes the new longitude with given distance traveled.

        Args:
            longitude (float): Last known longitude position
            latitude (float): Last known latitude position
            dy (float): Distance traveled in longitude direction

        Returns:
            float: New longitude position
        """
        return longitude + (dx / EARTH_RADIUS) * (180 / np.pi) / np.cos(latitude * np.pi / 180)

    def dy_dx_from_distance_and_heading(self, dist: float, heading: float) -> 'tuple[float, float]':
        """Calculates the distance traveled in latitude and longitude directions.

        Args:
            dist (float): Distance in meter. To compute translation in degree we need to convert dist to km.
            heading (float): Orientation of the vehicle relative to true north in degree (-180, 180)

        Returns:
            tuple[float, float]: Distance traveled in latitude direction (dy), Distance traveled in longitude direction (dx)
        """
        dist /= 1000
        dy = np.sin(np.pi / 2 - heading) * dist
        dx = np.cos(np.pi / 2 - heading) * dist

        return dy, dx

    def geo_distance(self, latitude1: float, longitude1: float, latitude2: float, longitude2: float) -> float:
        """Calculate the geographical distance between two points using the Haversine formula.

        Args:
            latitude1 (float): Latitude of point 1 in degree.
            longitude1 (float): Longitude of point 1 in degree.
            latitude2 (float): Latitude of point 2 in degree.
            longitude2 (float): Longitude of point 2 in degree.

        Returns:
            float: Spherical distance between the two points.
        """

        # Haversine formula:
        # https://en.wikipedia.org/wiki/Haversine_formula

        latitude1 = np.deg2rad(latitude1)
        latitude2 = np.deg2rad(latitude2)
        longitude1 = np.deg2rad(longitude1)
        longitude2 = np.deg2rad(longitude2)

        d_lon = longitude2 - longitude1
        d_lat = latitude2 - latitude1

        a = np.sin(d_lat / 2)**2 + np.cos(latitude1) * np.cos(latitude2) * np.sin(d_lon / 2)**2
        c = 2 * np.arcsin(np.sqrt(a))

        return c * EARTH_RADIUS

    def compare_position(self, cam: CAM, max_pos_err: float = POS_ERR_TOLERANCE,
                         max_heading_diff: float = HEADING_TOLERANCE) -> bool:
        """Compare the new position (from CAM) to check if it corresponds to this retraced vehicle.

        Args:
            cam (CAM): New position, heading and speed provided by the cam.
            max_pos_err (float): Max error for distance between target and estimated position based on new position in km.
            max_heading_diff (float): Max heading difference between two time stamps in radians

        Returns:
            bool: New position (from CAM) belongs to this vehicle.
        """

        delta_t = cam.timestamp - self.timestamps[-1]

        new_position = {'lat': cam.latitude * 10e-8, 'long': cam.longitude * 10e-8}  # Convert microdegrees to degrees
        old_position = {'lat': self.latitude[-1] * 10e-8, 'long': self.longitude[-1] * 10e-8}  # Convert microdegrees to degrees

        velocity = self.speed[-1] / 100  # Convert from cm/s to m/s
        velocity_2 = cam.speed / 100

        t = delta_t / 1000  # Convert from ms to s
        heading = np.deg2rad(self.heading[-1] / 10)  # Convert from decidegree to radians
        heading_2 = np.deg2rad(cam.heading / 10)
        dist = velocity * t / 2
        dist_2 = velocity_2 * t / 2
        dy_1, dx_1 = self.dy_dx_from_distance_and_heading(dist, heading)
        dy_2, dx_2 = self.dy_dx_from_distance_and_heading(dist_2, heading_2)
        dx = dx_1 + dx_2
        dy = dy_1 + dy_2

        estimated_longitude = self.compute_new_long(old_position['long'], old_position['lat'], dx)
        estimated_latitude = self.compute_new_lat(old_position['lat'], dy)

        position_deviation = self.geo_distance(new_position['lat'], new_position['long'], estimated_latitude, estimated_longitude)

        heading_in_constraint = False
        if position_deviation < max_pos_err:
            diff = (((heading_2 - heading) + np.pi / 2) % np.pi) - np.pi / 2
            heading_in_constraint = -max_heading_diff < diff < max_heading_diff

        return position_deviation < max_pos_err and heading_in_constraint

    def get_trace_duration(self, original_positions: 'list[Position]', traced_positions: 'list[Position]') -> int:
        """Compares the traced route and the original route and calculates the tracking duration.

        Args:
            original_positions (list[Position]): A list of the original positions with corresponding timestamps
            traced_positions (list[Position]): A list of the traced positions with corresponding timestamps

        Returns:
            duration (int): Total time the attacker traced the target correctly.
        """
        duration = 0
        for i in range(1, min(len(traced_positions), len(original_positions))):
            if traced_positions[i] != original_positions[i]:
                break

            old_timestamp = original_positions[i - 1].timestamp
            new_timestamp = original_positions[i].timestamp
            duration += new_timestamp - old_timestamp

        return duration

    # Update position and driving parameters with the new CAM
    def update_parameters(self, cam: CAM):
        self.speed.append(cam.speed)
        self.heading.append(cam.heading)
        self.longitude.append(cam.longitude)
        self.latitude.append(cam.latitude)
        self.pseudo_id.append(cam.pseudo_id)

        self.duration += cam.timestamp - self.timestamps[-1]
        self.timestamps.append(cam.timestamp)

    def get_positions(self) -> 'list[Position]':
        """Return the traced positions of the vehicle.

        Returns:
            list[Position]: The traced positions of the vehicle
        """
        return [Position(longitude=long_lat_time[0], latitude=long_lat_time[1], timestamp=long_lat_time[2]) for
                long_lat_time in zip(self.longitude, self.latitude, self.timestamps)]


# Class for original routes
class VehicleConstantId():
    def __init__(self, static_id: int, longitude: int, latitude: int, timestamp: int):
        self.static_id = static_id
        self.longitude = [longitude]
        self.latitude = [latitude]
        self.timestamps = [timestamp]
        self.duration = 0

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(sid={self.static_id}; t_max={self.duration})'

    def __repr__(self) -> str:
        return self.__str__()

    # Compare Static ID and update parameters in case of a match
    def try_update_parameters(self, id: int, longitude: int, latitude: int, timestamp: int) -> bool:
        if id != self.static_id:
            return False

        self.longitude.append(longitude)
        self.latitude.append(latitude)

        self.duration += timestamp - self.timestamps[-1]
        self.timestamps.append(timestamp)

        return True

    def get_positions(self) -> 'list[Position]':
        """Return the original positions of the vehicle.

        Returns:
            list[Position]: The original positions of the vehicle
        """
        return [Position(longitude=long_lat_time[0], latitude=long_lat_time[1], timestamp=long_lat_time[2]) for
                long_lat_time in zip(self.longitude, self.latitude, self.timestamps)]


def match_static_vehicle(cam: CAM, static_vehicles: 'list[VehicleConstantId]') -> 'Optional[VehicleConstantId]':
    is_known_veh = False
    for vehicle_constant in static_vehicles:
        is_known_veh = vehicle_constant.try_update_parameters(cam.static_id, cam.longitude, cam.latitude, cam.timestamp)
        if is_known_veh:
            break

    if is_known_veh:
        return None

    # Return new vehicle with static ID, if no available vehicle matched
    return VehicleConstantId(cam.static_id, cam.longitude, cam.latitude, cam.timestamp)


def match_dynamic_vehicle(cam: CAM, dynamic_vehicles: 'list[VehicleDynamicId]') -> 'Optional[VehicleDynamicId]':
    is_known_veh = False
    for vehicle_dynamic in dynamic_vehicles:
        is_known_veh = vehicle_dynamic.compare_id(cam.pseudo_id)

        if (not is_known_veh and vehicle_dynamic.compare_parameters(cam.length, cam.width)):
            is_known_veh = vehicle_dynamic.compare_position(cam)

        if is_known_veh:
            vehicle_dynamic.update_parameters(cam)
            break

    if is_known_veh:
        return None

    # Return new vehicle with dynamic ID, if no available vehicle matched
    return VehicleDynamicId(cam)


def build_routes(cams: 'list[CAM]', vehicles: Optional[list[int]] = None):
    static_vehicles: list[VehicleConstantId] = []
    dynamic_vehicles: list[VehicleDynamicId] = []

    # Find original and estimated CAM routes
    for cam in cams:
        if vehicles and cam.static_id not in vehicles:
            continue

        new_static_veh = match_static_vehicle(cam, static_vehicles)
        if new_static_veh:
            static_vehicles.append(new_static_veh)

        new_dynamic_veh = match_dynamic_vehicle(cam, dynamic_vehicles)
        if new_dynamic_veh:
            dynamic_vehicles.append(new_dynamic_veh)

    return static_vehicles, dynamic_vehicles


def get_vehicle_traces(cams: 'list[CAM]', vehicles: Optional[list[int]] = None,
                       max_vehicles: Optional[int] = None) -> 'list[VehicleTrace]':
    static_vehicles, dynamic_vehicles = build_routes(cams, vehicles)

    matched_vehicles: list[VehicleTrace] = []
    for original_trace in static_vehicles[:max_vehicles]:

        # check if more than 1 timestamp/position for vehicle static id exist
        if not len(set(original_trace.timestamps)) > 1:
            continue

        # check if static attacker reconstructed trace parts for static vehicle id exist
        reconstructed_traces: list[ReconstructedTrace] = []
        for target_trace in dynamic_vehicles:
            if (target_trace.static_id != original_trace.static_id
                    or len(set(target_trace.timestamps)) <= 1):
                continue

            # create reconstructed trace object for tracked trace part
            tracking_positions = target_trace.get_positions()
            original_positions = original_trace.get_positions()

            trace_duration = target_trace.get_trace_duration(original_positions, tracking_positions)
            trace_part = ReconstructedTrace(static_id=original_trace.static_id, pseudo_ids=target_trace.pseudo_id,
                                            positions=tracking_positions, duration=trace_duration)
            reconstructed_traces.append(trace_part)

        # check if reconstruction was successful
        if not reconstructed_traces:
            continue

        # construct original vehicle trace
        orig_trace = OriginalTrace(static_id=original_trace.static_id, positions=original_trace.get_positions(),
                                   duration=original_trace.duration)

        vehicle_trace = VehicleTrace(static_id=original_trace.static_id, original_trace=orig_trace,
                                     reconstructed_traces=reconstructed_traces)

        matched_vehicles.append(vehicle_trace)

    # write vehicle traces to file
    return matched_vehicles
