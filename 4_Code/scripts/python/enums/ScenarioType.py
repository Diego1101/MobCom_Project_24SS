# Python file with enum for scenario type

# @author  Annette Grueber (WS21/22)
# @author  Martin Dell (WS22/23)
# @date    15.11.2022

from enum import Enum


class ScenarioType(Enum):
    """Type of map/scenario of the simulation.
    """
    ESSLINGEN = 'esslingen'
    ESSLINGENEXT = 'esslingen_extension'
    ESSCOUNTRYROAD = 'ess_country_road'
    FREEWAYA8 = 'freeway_A8'

    def __str__(self):
        return self.value
