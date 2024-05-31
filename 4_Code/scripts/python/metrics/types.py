# All custom types for reconstructing and storing traces.

# @author  Leonie Heiduk (WS21/22)
# @author  Martin Mager (WS21/22)
# @author  Martin Dell (WS22/23)
# @author  Simon Seefeldt (WS22/23)
# @date    29.12.2022

class Position:
    """A geographic location at a point in time.
    """
    def __init__(self, longitude: int, latitude: int, timestamp: int):
        self.longitude = longitude
        self.latitude = latitude
        self.timestamp = timestamp

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False

        if self.longitude == other.longitude and self.latitude == other.latitude:
            return True

        return False

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(Long={self.longitude}; '
                f'Lat={self.latitude}; t={self.timestamp})')

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def microdeg_to_dd(value: int) -> float:
        """
        Convert micro degrees to decimal degrees.
        Decimal degrees (DD) express latitude and longitude geographic coordinates as decimal fractions.

        Args:
            value (int): Value to convert. E.g. `487433425`, `93201122`.

        Returns:
            float: Decimal degrees format of `value`. E.g. `48.7433425`, `9.3201122`.
        """
        return value / 1E7


class Trace:
    """A list of geographic locations which represent a vehicle's driven path.
    """
    def __init__(self, positions: 'list[Position]', duration: int):
        self.positions = positions  # list of positions
        self.duration = duration

    def __len__(self) -> int:
        return len(self.positions)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(N_Positions={len(self)}; t_max={self.duration})'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.__dict__})'

    def get_longitudes(self) -> 'list[int]':
        """Return the longitude values in micro degree format.
        """
        return [position.longitude for position in self.positions]

    def get_latitudes(self) -> 'list[int]':
        """Return the longitude values in micro degree format.
        """
        return [position.latitude for position in self.positions]

    def get_longitudes_as_gps(self) -> 'list[float]':
        """Return the longitude values in DD GPS format.
        """
        return [Position.microdeg_to_dd(position.longitude) for position in self.positions]

    def get_latitudes_as_gps(self) -> 'list[float]':
        """Return the latitude values in DD GPS format.
        """
        return [Position.microdeg_to_dd(position.latitude) for position in self.positions]

    def get_positions_as_gps(self) -> 'list[tuple[float, float]]':
        """Return the path as a tuple of latitude and longitude values in DD GPS format.

        Returns:
            list[tuple[float, float]]: Path as tuple of latitude and longitude values.
        """
        lat = self.get_latitudes_as_gps()
        long = self.get_longitudes_as_gps()

        return list(zip(lat, long))


class OriginalTrace(Trace):
    """Represents the original route based on the non-CAM parameter "static id"
    """
    def __init__(self, static_id: int, positions: 'list[Position]', duration: int):
        super().__init__(positions, duration)
        self.static_id = static_id

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(sid={self.static_id}; t_max={self.duration})'


class ReconstructedTrace(Trace):
    """Represents a trace part of the original route reconstructed by the static attacker
    """
    def __init__(self, static_id: int, pseudo_ids: 'list[int]', positions: 'list[Position]', duration: int):
        super().__init__(positions, duration)
        self.static_id = static_id
        self.pseudo_ids = pseudo_ids

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(sid={self.static_id}; t_max={self.duration})'


class VehicleTrace:
    """Mapping of original route and reconstructed trace parts based on the non-CAM parameter "static id"
    """
    def __init__(self, static_id: int, original_trace: OriginalTrace, reconstructed_traces: 'list[ReconstructedTrace]'):
        self.static_id = static_id
        self.original_trace = original_trace
        self.reconstructed_traces = reconstructed_traces

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(sid={self.static_id}; '
                f'original_trace={self.original_trace}; '
                'retraced_parts={len(self.reconstructed_traces)})')
