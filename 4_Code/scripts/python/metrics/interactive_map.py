# Functions to create interactive maps to visualize vehicles traces.

# @author  Martin Dell (WS22/23)
# @date    04.01.2022

import pandas as pd
from folium import Map, FeatureGroup, LayerControl, PolyLine, Marker, Icon
from folium.plugins import FeatureGroupSubGroup

from metrics.types import VehicleTrace
from metrics.utilities import get_pseudonym_changes


def get_route_stats(positions: 'list[tuple[float, float]]') -> 'tuple[list[float], list[float], list[float]]':
    """Returns the center, south west and north east point from given list of coordinates.

    Args:
        positions (list[tuple[float, float]]): Vehicles route points.

    Returns:
        tuple[list[float], list[float], list[float]]: SW, center, NE coordinates.
    """
    df = pd.DataFrame(positions, columns=['Lat', 'Long'])

    center = df[['Lat', 'Long']].mean().values.tolist() # type: ignore
    sw = df[['Lat', 'Long']].min().values.tolist() # type: ignore
    ne = df[['Lat', 'Long']].max().values.tolist() # type: ignore

    return sw, center, ne


def create_interactive_map(trace: VehicleTrace) -> Map:
    """Create an interactive map from given vehicle trace.

    Args:
        trace (VehicleTrace): Vehicle route to draw on the map.

    Returns:
        Map: Interactive map which can be saved to a html file.
    """
    original_route = trace.original_trace.get_positions_as_gps()
    original_start = original_route[0]

    reconstructed_route = trace.reconstructed_traces[0].get_positions_as_gps()

    sw, center, ne = get_route_stats(original_route)

    map = Map(center)

    fg_original_route = FeatureGroup('Original Route')
    fg_original_route.add_child(PolyLine(
        locations=original_route,
        color='blue',
        tooltip='Original Route',
    ))

    fg_traced_route = FeatureGroup('Reconstructed Route')
    fg_traced_route.add_child(PolyLine(
        locations=reconstructed_route,
        color='red',
        tooltip='Reconstructed Route',
    ))

    fg_pseudonyms = FeatureGroup('Pseudonym Change')
    # mark all positions in which the pseudonym was changed
    pseudonym_changes = get_pseudonym_changes(trace)
    for pseudonym, pos in pseudonym_changes.items():
        location = (pos[1], pos[0])
        if location == original_start:
            fg_original_route.add_child(Marker(
                location=original_start,
                tooltip=f'Start<br>{pseudonym}',
                icon=Icon(color='blue', icon='play', prefix='fa'),
            ))
        else:
            fg_pseudonyms.add_child(Marker(
                location=location,
                icon=Icon(color='gray', icon='shuffle', prefix='fa'),
                tooltip=str(pseudonym),
                opacity=0.75,
            ))

    map.add_child(fg_original_route)
    map.add_child(fg_traced_route)
    map.add_child(fg_pseudonyms)
    map.add_child(LayerControl(collapsed=False))

    map.fit_bounds([sw, ne])

    return map


def create_interactive_overview_map(vehicle_traces: 'list[VehicleTrace]') -> Map:
    """Create an interactive map which includes all given vehicle traces.

    Args:
        vehicle_traces (list[VehicleTrace]): Vehicle routes to draw on the map.

    Returns:
        Map: Interactive map which can be saved to a html file.
    """
    all_positions = [trace.original_trace.get_positions_as_gps() for trace in vehicle_traces]
    all_positions = [pos for positions in all_positions for pos in positions] # Flatten list

    sw, center, ne = get_route_stats(all_positions)

    map = Map(center)

    for trace in vehicle_traces:
        original_positions = trace.original_trace.get_positions_as_gps()

        fg = FeatureGroup(f'Vehicle #{trace.static_id}')

        fg_original_route = FeatureGroupSubGroup(fg, 'Original Route')
        fg_original_route.add_child(PolyLine(
            locations=original_positions,
            color='blue',
            tooltip=f'Original Route #{trace.static_id}',
        ))

        fg_original_route.add_child(Marker(
            location=original_positions[0],
            tooltip=f'Start #{trace.static_id}',
            icon=Icon(color='blue', icon='play', prefix='fa'),
        ))

        fg_traced_route = FeatureGroupSubGroup(fg, 'Reconstructed Route')
        fg_traced_route.add_child(PolyLine(
            locations=trace.reconstructed_traces[0].get_positions_as_gps(),
            color='red',
            tooltip=f'Reconstructed Route #{trace.static_id}',
        ))

        fg.add_child(fg_original_route)
        fg.add_child(fg_traced_route)
        map.add_child(fg)

    map.add_child(LayerControl(collapsed=False))

    map.fit_bounds([sw, ne])

    return map
