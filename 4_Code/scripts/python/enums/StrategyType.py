# Python file with enum for strategy type

# @author  Marek Parucha (WS21/22)
# @author  Martin Dell (WS22/23)
# @date    15.11.2022

from enum import Enum


class StrategyType(Enum):
    """Type of attacker in the simulation.
    """
    NO_ATTACKER = 'no_attacker'
    ATTACKER_SERVICE = 'attacker_service'

    def __str__(self) -> str:
        return self.value
