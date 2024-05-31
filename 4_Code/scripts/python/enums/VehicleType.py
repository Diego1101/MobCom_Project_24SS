# Python file with enum for vehicle type

# @author  Martin Dell (WS22/23)
# @date    23.11.2022

from enum import Enum


class VehicleType(Enum):
    """Type of vehicle in the simulation.
    """
    PASSENGER = 'passenger'
    TRUCK = 'truck'
    BUS = 'bus'
    MOTORCYCLE = 'motorcycle'
    BICYCLE = 'bicycle'
    EMERGENCY = 'emergency'
    TAXI = 'taxi'
    DELIVERY = 'delivery'

    # More vehicles classes according to
    # https://en.wikipedia.org/wiki/Euro_Car_Segment
    PASSENGER_A = 'passenger_a'
    PASSENGER_B = 'passenger_b'
    PASSENGER_C = 'passenger_c'
    PASSENGER_D = 'passenger_d'
    PASSENGER_E = 'passenger_e'
    PASSENGER_F = 'passenger_f'
    PASSENGER_J = 'passenger_j'
    PASSENGER_M = 'passenger_m'
    PASSENGER_S = 'passenger_s'

    def __str__(self) -> str:
        return self.value
