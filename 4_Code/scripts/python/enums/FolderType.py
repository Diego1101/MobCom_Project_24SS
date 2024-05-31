# Python file with enum for folder type

# @author  Annette Grueber (WS21/22)
# @author  Martin Dell (WS22/23)
# @date    15.11.2021

from enum import Enum


class FolderType(Enum):
    """Reference to a folder used in the simulation.
    """
    SCENARIO = 1
    LOGS = 2
    TRAFFIC = 3
    TEMP = 4
