# Python file with enum for pseudochange types

# @author  Marek Parucha (WS21/22)
# @author  Martin Dell (WS22/23)
# @author  Janis Latus (WS22/23)
# @date    24.11.2022

from enum import Enum


class PseudoChangeType(Enum):
    """Type of pseudonym change strategy.
    """
    NONE = 'no_change'
    SLOW = 'slow'
    PERIODICAL = 'periodical'
    DISTANCE = 'distance'
    WHISPER = 'whisper'
    CPN = 'cpn'

    def __str__(self) -> str:
        return self.value
