# Python file containing all constant information about traffic or needed in SUMO

# @author  Martin Dell (WS22/23)
# @date    20.12.2022

from enums.VehicleType import VehicleType


# The vehicle type distribution tells the the application how many trips and
# therefore vehicles you want in the simulation of this exact type.
# A value of 0.8 means that of all vehicles in the simulation,
# roughly 80 % will be of this type.
# All vehicle type probabilities in the distribution should add up to 1, i.e. 100 %.
# If this is not the case the application normalizes all probabilities automatically so that they add up 1.
vehicle_type_distribution = {
    VehicleType.PASSENGER_A: 0.1,
    VehicleType.PASSENGER_B: 0.2,
    VehicleType.PASSENGER_C: 0.2,
    VehicleType.PASSENGER_D: 0.2,
    VehicleType.PASSENGER_E: 0.03,
    VehicleType.PASSENGER_F: 0.03,
    VehicleType.PASSENGER_J: 0.02,
    VehicleType.PASSENGER_M: 0.03,
    VehicleType.PASSENGER_S: 0.01,
    VehicleType.TRUCK: 0.02,
    VehicleType.BUS: 0.03,
    VehicleType.MOTORCYCLE: 0.08,
    VehicleType.BICYCLE: 0.05,
}

# Dynamic attacker configuration
attacker = {
    'id': 'Rand_Attacker',          # SUMO Id
    'type': VehicleType.MOTORCYCLE, # Type of vehicle the attacker drives in
}

# Increase value, that vehicle tend to spawn more likely at the border of the map.
FRINGE_FACTOR = 10

# Minimum travel distance of a single vehicle in meters.
MIN_TRIP_DISTANCE = 50

# Despawn rate per tick, amount = 1/rate.
DESPAWN_RATE = 1

# 25% extra trips will be generated per vehicle type because some may be deleted due to e.g. invalid edges.
# Excess trips will not be included in the final step.
EXTRA_TRIP_BUFFER = 0.25

# Standard trip attributes for every trip.
# Must be valid SUMO trip XML attributes.
trip_attributes = {
    'departLane': 'best',
    'departSpeed': 'max',
}

# Timeout in seconds for generating trips for one vehicle type.
TRIP_GENERATION_TIMEOUT = 900  # 15 min

# Default color for vehicles
default_color = 'grey'

# Custom vtype parameter to define more vehicle classes in SUMO
# Clases according to https://en.wikipedia.org/wiki/Euro_Car_Segment

# Calculating accel (m/s^2):
# E.g. 0-100km/h in 14.7s
# 100km/h = 27.78 m/s
# accel = 27.78 / 14.7 = 1.9

# All keys and values must be valid SUMO vType attributes.
# See https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html#available_vtype_attributes

vtypes = {
    # Default SUMO vehicle
    VehicleType.PASSENGER: {
        'color': '129,129,129',
    },

    VehicleType.TRUCK: {
        'color': '255,150,0',
    },

    VehicleType.BUS: {
        'color': '20,183,30',
    },

    VehicleType.MOTORCYCLE: {
        'color': 'red',
    },

    VehicleType.BICYCLE: {
        'color': 'yellow',
    },

    VehicleType.EMERGENCY: {
        'color': 'blue',
    },

    VehicleType.DELIVERY: {
        'color': 'green',
    },

    # https://www.auto-data.net/de/fiat-panda-iii-city-cross-1.0-70hp-mhev-39071
    VehicleType.PASSENGER_A: {
        'vClass': VehicleType.PASSENGER,
        'guiShape': 'passenger/hatchback',
        'color': default_color,
        'length': 3.7,
        'width': 1.7,
        'height': 1.6,
        'maxSpeed': 43.1, # 155km/h
        'accel': 1.9, # 0-100km/h in 14.7s,
    },

    # https://www.auto-data.net/de/volkswagen-polo-vi-facelift-2021-1.0-evo-80hp-45894
    VehicleType.PASSENGER_B: {
        'vClass': VehicleType.PASSENGER,
        'guiShape': 'passenger/hatchback',
        'color': default_color,
        'length': 4.1,
        'width': 1.8,
        'height': 1.4,
        'maxSpeed': 47.5, # 171km/h
        'accel': 1.8, # 0-100km/h in 15.5s
    },

    # https://www.auto-data.net/de/volkswagen-golf-vii-3-door-1.4-tsi-act-140hp-dsg-45056
    VehicleType.PASSENGER_C: {
        'vClass': VehicleType.PASSENGER,
        'guiShape': 'passenger/hatchback',
        'color': default_color,
        'length': 4.3,
        'width': 1.8,
        'height': 1.5,
        'maxSpeed': 58.9, # 212km/h
        'accel': 3.3, # 0-100km/h in 8.4s
    },

    # https://www.auto-data.net/de/bmw-3-series-sedan-g20-lci-facelift-2022-m340i-374hp-mhev-xdrive-steptronic-45839
    VehicleType.PASSENGER_D: {
        'vClass': VehicleType.PASSENGER,
        'guiShape': 'passenger/sedan',
        'color': default_color,
        'length': 4.7,
        'width': 1.8,
        'height': 1.4,
        'maxSpeed': 69.4, # 250km/h
        'accel': 6.3, # 0-100km/h in 4.4s
    },

    # https://www.auto-data.net/de/mercedes-benz-e-class-w213-facelift-2020-e-400d-330hp-4matic-9g-tronic-40978
    VehicleType.PASSENGER_E: {
        'vClass': VehicleType.PASSENGER,
        'guiShape': 'passenger/sedan',
        'color': default_color,
        'length': 4.9,
        'width': 1.9,
        'height': 1.5,
        'maxSpeed': 69.4, # 250km/h
        'accel': 5.7, # 0-100km/h in 4.9s
    },

    # https://www.auto-data.net/de/mercedes-benz-s-class-w223-s-400d-330hp-4matic-9g-tronic-41087
    VehicleType.PASSENGER_F: {
        'vClass': VehicleType.PASSENGER,
        'guiShape': 'passenger/sedan',
        'color': default_color,
        'length': 5.2,
        'width': 1.9,
        'height': 1.5,
        'maxSpeed': 69.4, # 250km/h
        'accel': 5.1, # 0-100km/h in 5.4s
    },

    # https://www.auto-data.net/de/audi-q5-sportback-35-tdi-163hp-mhev-s-tronic-42290
    VehicleType.PASSENGER_J: {
        'vClass': VehicleType.PASSENGER,
        'guiShape': 'passenger',
        'color': default_color,
        'length': 4.7,
        'width': 1.9,
        'height': 1.6,
        'maxSpeed': 59.2, # 213km/h
        'accel': 3.1, # 0-100km/h in 9.0s
    },

    # https://www.auto-data.net/de/volkswagen-cross-touran-i-facelift-2010-2.0-tdi-140hp-20455
    VehicleType.PASSENGER_M: {
        'vClass': VehicleType.PASSENGER,
        'guiShape': 'passenger/wagon',
        'color': default_color,
        'length': 4.4,
        'width': 1.8,
        'height': 1.7,
        'maxSpeed': 53.9, # 194km/h
        'accel': 2.7, # 0-100km/h in 10.3s
        'emissionClass': 'HBEFA3/PC_D_EU5', # Diesel Euro 5
    },

    # https://www.auto-data.net/de/porsche-911-992-carrera-t-3.0-385hp-46702
    VehicleType.PASSENGER_S: {
        'vClass': VehicleType.PASSENGER,
        'guiShape': 'passenger',
        'color': default_color,
        'length': 4.5,
        'width': 1.9,
        'height': 1.3,
        'maxSpeed': 80.8, # 291km/h
        'accel': 6.2, # 0-100km/h in 4.5s
    },
}


def get_vclass(vehicle_type: VehicleType) -> str:
    """
    Returns the vClass of given vehicles type.
    The vClass represents the base type of a vehicle type.

    Args:
        vehicle_type (VehicleType): The vehicle type.

    Returns:
        str: Its vClass or 'passenger' if no specific vClass was defined.
    """

    attributes = vtypes.get(vehicle_type, {})
    return str(attributes.get('vClass', VehicleType.PASSENGER))
