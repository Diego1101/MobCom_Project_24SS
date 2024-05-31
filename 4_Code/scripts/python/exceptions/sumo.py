# Exceptions when generating routes with SUMO

# @author  Martin Dell (WS22/23)
# @date    25.12.2022

from typing import Optional


class UnconfiguredEnvironmentError(Exception):
    """Exception for when a environment variable is not correctly setup or missing
    """
    pass


class TripNotFoundError(Exception):
    """Exception for when a trip is not found.
    """
    def __init__(self, message: str, trip_id: Optional[str] = None):
        super().__init__(message)

        self.trip_id = trip_id


class NoTripsError(Exception):
    """Exception for when no SUMO trips where found or generated.
    """
    pass
