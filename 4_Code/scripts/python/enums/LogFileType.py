# Python file with enum for log file types

# @author  Martin Dell (WS22/23)
# @date    22.12.2022

from enum import Enum


class LogFileType(Enum):
    """Type of log file.
    """
    SUMO = 1
    TRACI = 2
    DUAROUTER = 3
