# Utility function used to generate SUMO trips.

# @author  Martin Dell (WS22/23)
# @date    21.11.2022

import os
import shutil
import contextlib
from collections import OrderedDict
from collections.abc import Iterable
from typing import Any
from enums.FolderType import FolderType
from enums.VehicleType import VehicleType
from generators.types import Trip
from utils.configuration import SimConfig
import utils.PathUtil as PathUtil
import constants.traffic as traffic
import xml.etree.ElementTree as ET


def normalize_vehicle_distribution(distribution: 'dict[VehicleType, float]') -> 'dict[VehicleType, float]':
    """Normalizes all distribution so that the sum of all vehicle classes adds up to 1.

    Args:
        distribution (dict[VehicleType, float]): Vehicle distributions

    Returns:
        dict[VehicleType, float]: Normalized vehicle distributions
    """
    normalized_distribution = {}

    total = sum(distribution.values())
    for (veh_type, dist) in distribution.items():
        normalized_distribution[veh_type] = dist / total

    return normalized_distribution


def normalize_spawn_distribution(distribution: 'list[float]') -> 'list[float]':
    """The given spawn_distribution is normalized to 1 by this method.
    """
    return [i / sum(distribution) for i in distribution]


def remove_temp_files(cfg: SimConfig):
    """Cleans up all created temporary files and directories.

    Args:
        cfg (SimConfig): Simulation config.
    """
    temp_dir = PathUtil.get_path(FolderType.TEMP, cfg, must_exist=False)

    # Delete temp files and folder
    shutil.rmtree(temp_dir, ignore_errors=True)

    # For some reason temp dir is not removed by rmtree sometimes
    with contextlib.suppress(FileNotFoundError):
        os.removedirs(temp_dir)


def generate_vtype(veh_type: VehicleType) -> str:
    """Generates the corresponding SUMO vtype XML string for given vehicle type.

    Args:
        veh_type (VehicleType): Vehicle type fo which to generate vtype.

    Returns:
        str: vtype of vehicle type as XML string.
    """
    attributes: OrderedDict[str, Any] = OrderedDict(traffic.vtypes.get(veh_type, {}))
    # Set min attributes if not available
    attributes.setdefault('id', veh_type)
    attributes.setdefault('vClass', veh_type)
    attributes.setdefault('color', traffic.default_color)

    return toxml('vType', attributes)


def toxmlattr(attributes: 'dict[str, Any]') -> 'list[str]':
    """
    Converts the given attributes dictionary to a list of XML attributes
    in the format of `key=\"value\"`.

    Args:
        attributes (dict[str, Any]): Key value attributes.

    Returns:
        list[str]: List of XML attributes string as `key=\"value\"`.
    """
    return [f'{key}=\"{value}\"' for key, value in attributes.items()]


def toxml(tag: str, attributes: 'dict[str, Any]') -> str:
    """Converts the attributes to a XML tag string.

    Args:
        tag (str): The XML tag, i.e. `<tag />`.
        attributes (dict[str, Any]): Key value attributes.

    Returns:
        str: XML tag string in the format `<tag key=\"value\" key=\"value\" ... />`.
    """
    xml = f'<{tag} '
    xml += ' '.join(toxmlattr(attributes))
    xml += '/>'

    return xml


def parse_trips(file: str, trip_id_prefix: str = '') -> 'list[Trip]':
    """
    Opens `file` and parses its content to a list of trips as XML strings.

    Args:
        file (str): Path to the generated trips by the sumo script.

    Returns:
        list[str]: List of trips as XML strings
    """
    tree = ET.parse(file)
    routes = tree.getroot()

    return [Trip.from_xml(trip.attrib, trip_id_prefix) for trip in routes.findall(Trip.xml_tag)]


def count_trips(file_path: str) -> int:
    """Count the trips defined in given file.

    Args:
        file (str): Files containing trips.

    Returns:
        int: Number of trips defined in the file.
    """
    n_trips = 0
    trip_identifier = f'<{Trip.xml_tag}'

    with open(file_path, 'r') as f:
        for line in f:
            if trip_identifier in line:
                n_trips += 1

    return n_trips


class TripXmlWriter:
    """Class for writing trips in XML format.
    """
    def __init__(self, output_file: str, vehicle_types: 'Iterable[VehicleType]'):
        self.output_file = output_file
        self.vehicle_types = vehicle_types

    def generate_vehicle_types(self) -> 'list[str]':
        """Generates the vType string of vehicle-classes that are used at all given trips.

        Returns:
            list[str]: XML vTypes
        """
        return [generate_vtype(veh_type) for veh_type in self.vehicle_types]

    def generate_header(self) -> str:
        """Generates the xml-header string

        Returns:
            str: XML header
        """
        res = '<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n\n'
        res += '<routes xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"http://sumo.dlr.de/xsd/routes_file.xsd\">\n'
        return res

    def generate_trailer(self) -> str:
        """Generates the xml-trailer string

        Returns:
            str: XML trailer
        """
        return '</routes>\n'

    def write(self, trips: 'Iterable[Trip]'):
        """Write `trips` to given file.

        Args:
            file_path (str): File where to write the trips to.
            trips (Iterable[Trip]): List of trips.
        """
        with open(self.output_file, 'w') as f:
            f.write(self.generate_header())

            for vtype in self.generate_vehicle_types():
                f.write('    ' + vtype + '\n')

            for trip in trips:
                f.write('    ' + str(trip) + '\n')

            f.write(self.generate_trailer())
