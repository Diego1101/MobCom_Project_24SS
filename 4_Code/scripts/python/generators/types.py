# Types used to represent SUMO trips

# @author  Martin Dell (WS22/23)
# @date    23.12.2022

from __future__ import annotations
from collections import OrderedDict
from enums.VehicleType import VehicleType
import generators.helper as helper


class Trip:
    """
    Simple class that represents a SUMO trip/route.

    Args:
        id (str): Trip ID.
        depart_time (float): Point in time where the vehicle will spawn in seconds. Will be rounded to two decimal places.
        type (VehicleType): Type of vehicle which will drive on this route.
        depart_lane (str): This can be "best" or the lane number of the spawn edge (e.g. 0).
        depart_speed (str): This can be "max" or a float representing speed.
        from_edge (str): SUMO-edge where the vehicle will spawn.
        to_edge (str): SUMO-edge where the vehicle will despawn.
    """
    def __init__(self,
                 id: str,
                 type: VehicleType,
                 depart_time: float,
                 depart_lane: str,
                 depart_speed: str,
                 from_edge: str,
                 to_edge: str):

        self._attributes = OrderedDict()
        self._attributes['id'] = id
        self._attributes['type'] = type
        self._attributes['depart'] = round(depart_time, 2)
        self._attributes['departLane'] = depart_lane
        self._attributes['departSpeed'] = depart_speed
        self._attributes['from'] = from_edge
        self._attributes['to'] = to_edge

    xml_tag = 'trip'

    @property
    def id(self) -> str:
        return self._attributes['id']

    @property
    def veh_type(self) -> VehicleType:
        return self._attributes['type']

    @property
    def depart_time(self) -> float:
        return self._attributes['depart']

    @property
    def depart_lane(self) -> str:
        return self._attributes['departLane']

    @property
    def depart_speed(self) -> str:
        return self._attributes['departSpeed']

    @property
    def from_edge(self) -> str:
        return self._attributes['from']

    @property
    def to_edge(self) -> str:
        return self._attributes['to']

    def __repr__(self) -> str:
        return f'Trip(id={self.id} depart={self.depart_time:f.2})'

    def __str__(self) -> str:
        """Converts the trip to SUMO string representation

        Returns:
            String: SUMO trip xml string
        """
        return helper.toxml(self.xml_tag, self._attributes)

    def __eq__(self, other) -> bool:
        if isinstance(other, Trip):
            return self.id == other.id

        return False

    @staticmethod
    def from_xml(xml_attributes: 'dict[str, str]', trip_id_prefix: str = '') -> Trip:
        """Builds a `Trip` object from passed XML attributes.

        Args:
            xml_attributes (dict[str, str]): XML attributes of a SUMO trip.
            trip_id_prefix (str, optional): Prefix to add to the trip id. Defaults to no prefix.

        Returns:
            Trip: SUMO trip object.
        """

        kwargs = {
            'id': trip_id_prefix + xml_attributes['id'],
            'type': VehicleType[xml_attributes['type'].upper()],
            'depart_time': float(xml_attributes['depart']),
            'depart_lane': xml_attributes['departLane'],
            'depart_speed': xml_attributes['departSpeed'],
            'from_edge': xml_attributes['from'],
            'to_edge': xml_attributes['to'],
        }
        return Trip(**kwargs)
