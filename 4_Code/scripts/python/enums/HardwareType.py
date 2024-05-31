# Python file with enum for pseudochange types

# @author  Marek Parucha (WS21/22)
# @author  Martin Dell (WS22/23)
# @date    15.11.2022

from enum import Enum


class HardwareType(Enum):
    """Type of hardware used in the simulation.
    """
    NONE = 'no_hw'
    COHDA = 'cohda'

    def __str__(self) -> str:
        return self.value
