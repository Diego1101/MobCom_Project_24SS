# Python file with enum for file type

# @author  Annette Grueber (WS21/22)
# @author  Martin Dell (WS22/23)
# @date    23.11.2022

from enum import Enum


class FileType(Enum):
    """Reference to a file used in the simulation.
    """
    SUMO_CONFIG_TEMPLATE = 1
    NET = 2
    VIEW = 3
    ADD = 4
    ROUTE = 5
    OMNET_INI_TEMPLATE = 6
    NED = 7
    LIBRARY = 8
    RESULTS = 9
    DEN_USE_CASE = 10
    VALIDATED_ROUTE = 11
    CMAKE_PARENT_TEMPLATE = 12
    CMAKE_CHILD_TEMPLATE = 13
    SERVICE_TEMPLATE = 14
    GLOBAL_CONFIG = 15
    ARTERY_SENSORS = 16
    ATTACKER_INFO = 17
