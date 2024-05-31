# Exceptions when configuring hardware integration

# @author  Martin Dell (WS22/23)
# @date    11.02.2023

class NoHardwareVehicleIdError(Exception):
    """Exception for when hardware integration is enabled but vehicle id is not set.
    """
    pass
