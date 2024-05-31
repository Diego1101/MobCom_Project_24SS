# Utility functions used to reconstruct traces.

# @author  Leonie Heiduk (WS21/22)
# @author  Martin Mager (WS21/22)
# @author  Martin Dell (WS22/23)
# @date    29.11.2022

import csv
import os
from typing import Any
import yaml
import constants.paths as cpaths
from metrics.types import VehicleTrace


class CAM:
    """Wrapper for one CAM.
    """
    def __init__(self, timestamp: int, static_id: int, pseudo_id: int, longitude: int, latitude: int,
                 width: int, length: int, speed: int, heading: int):
        self.timestamp = timestamp
        self.static_id = static_id
        self.pseudo_id = pseudo_id
        self.longitude = longitude
        self.latitude = latitude
        self.width = width
        self.length = length
        self.heading = heading
        self.speed = speed

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(sid={self.static_id}; '
                f'pid={self.pseudo_id}; t={self.timestamp})')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.__dict__})'

    @staticmethod
    def from_csv(csv_row: 'list[str]'):
        """Parse CAM from one CSV log row.

        Args:
            csv_row (list[str]): CSV row as list of columns.

        Returns:
            CAM: Parsed cam from CSV row.
        """
        # Timestamp, ServiceID, Pseudonym, Longitude, Latitude, Width, Length, Speed, Heading
        return CAM(int(csv_row[0]), int(csv_row[1]), int(csv_row[2]), int(csv_row[3]), int(csv_row[4]),
                   int(csv_row[5]), int(csv_row[6]), int(csv_row[7]), int(csv_row[8]))


def parse_cam_csv(path: str) -> 'list[CAM]':
    """Parses the recorded CAMs in `result.csv` to a list of CAM object.

    Args:
        scenario_path (_type_): Path to the result folder of the simulation run
        where the `result.csv` is located.

    Returns:
        list[CAM]: Parsed recorded CAMs.
    """

    # Read result.csv and parse data into matrix
    with open(path) as f:
        reader = csv.reader(f)
        next(reader, None) # Skip header

        return [CAM.from_csv(row) for row in reader]


def remove_duplicates_in_csv(in_csv_file: str, out_csv_file: str):
    """Removes all duplicate rows in the csv.

    Args:
        in_csv_file (str): Path of the source CSV where duplicates should be removed.
        out_csv_file (str): Path to the output CSV used to save the result.
    """
    with open(in_csv_file, 'r') as in_file, open(out_csv_file, 'w') as out_file:
        seen = set()
        for line in in_file:
            if line in seen:
                continue

            seen.add(line)
            out_file.write(line)


def remove_duplicate_cam(cam_csv_path: str):
    """Removes all duplicate CAMs in given file.

    Args:
        cam_csv_path (str): Path to a CSV containing CAMs.
    """
    tmp_file = os.path.join(os.path.dirname(cam_csv_path), cpaths.cam_temp_csv)

    remove_duplicates_in_csv(cam_csv_path, tmp_file)

    os.remove(cam_csv_path)
    os.rename(tmp_file, cam_csv_path)


def parse_config(cfg_file: str) -> 'dict[str, Any]':
    """Return YAML config file as dictionary.

    Args:
        cfg_file (str): Path to YAML config file.

    Returns:
        dict[str, Any]: Contents of YAML file as dictionary.
    """
    with open(cfg_file, 'r') as yaml_file:
        return yaml.safe_load(yaml_file)


def get_pseudonym_changes(vehicle_trace: VehicleTrace) -> 'dict[int, tuple[float, float]]':
    """Return the pseudonym changes the given vehicle has made and those positions.

    Args:
        vehicle_trace (VehicleTrace): Vehicle trace.

    Returns:
        dict[int, tuple[float, float]]: Key is pseudonym and value is the first position
                                        (long, lat) where the pseudonym it was changed to.
    """
    # mark all positions in which the pseudonym was changed
    pseudonym_changes: dict[int, tuple[float, float]] = {}
    for part in vehicle_trace.reconstructed_traces:
        part_longitudes = part.get_longitudes_as_gps()
        part_latitudes = part.get_latitudes_as_gps()

        # Find all first occurrences of pseudonym changes and their location
        pseudo_ids = set(part.pseudo_ids)
        for pseudo_id in pseudo_ids:
            # find location of pseudo change -> plot mark + text(pseudoID)
            idx = part.pseudo_ids.index(pseudo_id)
            pseudonym_changes.setdefault(pseudo_id, (part_longitudes[idx], part_latitudes[idx]))

    return pseudonym_changes
