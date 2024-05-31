# Evaluates the static attacker by visualizing the reconstructed routes of vehicles.

# @author  Leonie Heiduk (WS21/22)
# @author  Martin Mager (WS21/22)
# @author  Martin Dell (WS22/23)
# @date    03.12.2022

import os
import random
import shutil
from argparse import Namespace

import constants.paths as cpaths
from joblib import Parallel, delayed
from matplotlib import pyplot as plt
from metrics.gps_visualizer import GPSVisualizer
from metrics.types import Position, VehicleTrace
from metrics.utilities import get_pseudonym_changes
import metrics.interactive_map as imap
from PIL import Image, ImageDraw


def evaluate(args: Namespace, traces: 'list[VehicleTrace]', **kwargs):
    """Evaluates the static attacker. Creates plots to visualizes reconstructed routes.

    Args:
        args (Namespace): Evaluation configuration.
        traces (list[VehicleTrace]): Reconstructed routes of vehicles.
    """
    # create static attacker sub-folder
    static_attacker_dir = os.path.join(args.sim_dir, cpaths.metrics_dirname, cpaths.static_attacker_dirname)
    os.makedirs(static_attacker_dir, exist_ok=True)

    print('Evaluating all vehicle traces...')

    with Parallel(n_jobs=args.n_jobs, verbose=10) as parallel:
        delayed_fncs = [delayed(evaluate_trace)(trace,
                                                traces,
                                                static_attacker_dir,
                                                args.create_interactive_map)
                        for trace in traces]

        tracking_successes: list[float] = parallel(delayed_fncs)  # type: ignore

    # overview of all traces ###########################################################################################
    print('Drawing overview map...')

    scenario_esslingen_map = os.path.join(static_attacker_dir, cpaths.esslingen_map_filename)
    # copy map to scenario/metrics folder -> later used to visualize all vehicle traces in one single map
    shutil.copy2(cpaths.esslingen_map, scenario_esslingen_map)
    draw_overview_map(scenario_esslingen_map, traces)

    # Create interactive overview map

    print('Create interactive map...')
    html_map = imap.create_interactive_overview_map(traces)
    html_map.save(os.path.join(static_attacker_dir, cpaths.esslingen_imap_filename))

    print('Writing metrics...')

    # write metrics for complete scenario to file
    with open(os.path.join(static_attacker_dir, cpaths.tracking_success), 'w') as result_file:
        tracking_success = (sum(tracking_successes) / len(traces)) * 100
        result_file.write(f'Tracking success: {tracking_success:.2f} [%]')

    print(f'Overall tracking success: {tracking_success:3.2f} %')


def evaluate_trace(vehicle_trace: VehicleTrace, vehicle_traces: 'list[VehicleTrace]',
                   static_attacker_dir: str, create_interactive_map: bool = False) -> float:
    """Plots the evaluation for one vehicles.

    Args:
        vehicle_trace (VehicleTrace): Vehicle route and trace of the vehicle.
        vehicle_traces (list[VehicleTrace]): All routes and traces.
        static_attacker_dir (str): Directory where to save the plots to.
        create_interactive_map (bool, optional): If an interactive map should be created. Defaults to False.

    Returns:
        float: Tracking success of vehicle.
    """
    # create folder structure
    result_dir = os.path.join(static_attacker_dir, str(vehicle_trace.static_id))
    os.makedirs(result_dir, exist_ok=True)

    # plot "original trace", "reconstructed trace" and "comparison original vs reconstructed"
    fig = plt.figure()
    fig.set_size_inches(30, 5)
    ax_org_trace = fig.add_subplot(131)
    ax_re_trace = fig.add_subplot(132, sharex=ax_org_trace, sharey=ax_org_trace)
    ax_comp = fig.add_subplot(133, sharex=ax_org_trace, sharey=ax_org_trace)

    # original trace plot ##############################################################################################
    plot_original_trace(ax_org_trace, vehicle_trace)

    # reconstructed trace plot of the target route until it is lost e.g. after a pseudo change ##########################
    plot_reconstructed_trace(ax_re_trace, vehicle_trace)

    # comparison plot ##################################################################################################
    plot_comparison(ax_comp, vehicle_trace)

    # save figures
    fig.tight_layout()
    fig.savefig(os.path.join(result_dir, f'plot_{vehicle_trace.static_id}.png'), dpi=200)

    # map part #########################################################################################################
    draw_map(vehicle_trace, vehicle_traces, result_dir)

    if create_interactive_map:
        html_map = imap.create_interactive_map(vehicle_trace)
        html_map.save(os.path.join(result_dir, f'map_{vehicle_trace.static_id}.html'))

    tracking_success = write_success_rate(vehicle_trace, result_dir)

    print(f'Vehicle #{vehicle_trace.static_id:<5} Tracking success: {(tracking_success * 100):>6.2f} %')

    return tracking_success


def plot_original_trace(ax: plt.Axes, vehicle_trace: VehicleTrace):
    """Plot the original route of the vehicle.
    """
    ax.set_title(f'Original route (Static ID: {vehicle_trace.static_id})')
    ax.set(xlabel='Longitude', ylabel='Latitude')
    ax.ticklabel_format(useOffset=False)
    ax.set_aspect('equal', 'box')

    # data
    longitudes = vehicle_trace.original_trace.get_longitudes_as_gps()
    latitudes = vehicle_trace.original_trace.get_latitudes_as_gps()

    ax.scatter(longitudes, latitudes, marker='.', c='grey', label='Original route')
    ax.annotate('Start', (longitudes[0], latitudes[0]))
    ax.legend()


def plot_reconstructed_trace(ax: plt.Axes, vehicle_trace: VehicleTrace):
    """Plot the reconstructed route of the vehicle.
    """
    ax.set_title(f'Reconstructed trace (Static ID: {vehicle_trace.static_id})\n'
                 f'Max. tracking duration: {vehicle_trace.reconstructed_traces[0].duration} ms')
    ax.set(xlabel='Longitude', ylabel='Latitude')
    ax.set_aspect('equal', 'box')
    ax.ticklabel_format(useOffset=False)

    # data
    longitudes = vehicle_trace.reconstructed_traces[0].get_longitudes_as_gps()
    latitudes = vehicle_trace.reconstructed_traces[0].get_latitudes_as_gps()

    ax.scatter(longitudes, latitudes, marker='.', label='Reconstructed route')
    ax.annotate('Start', (longitudes[0], latitudes[0]))
    ax.legend()


def plot_comparison(ax: plt.Axes, vehicle_trace: VehicleTrace):
    """Plot a comparison of the original and reconstructed route of the vehicle.
    """
    ax.set_title(f'Comparison (Static ID: {vehicle_trace.static_id})')
    ax.set(xlabel='Longitude', ylabel='Latitude')
    ax.set_aspect('equal', 'box')
    ax.ticklabel_format(useOffset=False)

    original_long = vehicle_trace.original_trace.get_longitudes_as_gps()
    original_lat = vehicle_trace.original_trace.get_latitudes_as_gps()

    # original route
    ax.plot(original_long, original_lat, 'k', alpha=0.2, linewidth=8, label='Original route')

    traced_long = vehicle_trace.reconstructed_traces[0].get_longitudes_as_gps()
    traced_lat = vehicle_trace.reconstructed_traces[0].get_latitudes_as_gps()

    # reconstructed trace for static id
    ax.scatter(traced_long, traced_lat, marker='.', label='Reconstructed route')

    # mark all positions in which the pseudonym was changed
    pseudonym_changes = get_pseudonym_changes(vehicle_trace)

    pc_long = [pc[0] for pc in pseudonym_changes.values()]
    pc_lat = [pc[1] for pc in pseudonym_changes.values()]

    ax.scatter(pc_long, pc_lat, c='black', marker='*', label='Pseudonym Change')

    for pseudonym, pos in pseudonym_changes.items():
        ax.annotate(str(pseudonym), pos, xytext=(2, -14), textcoords='offset points')

    ax.legend()


def draw_map(vehicle_trace: VehicleTrace, vehicle_traces: 'list[VehicleTrace]', result_dir: str):
    """Draws the routes of one vehicle onto a static map.

    Args:
        vehicle_trace (VehicleTrace): Routes of the vehicle to draw.
        vehicle_traces (list[VehicleTrace]): Routes of all vehicles.
        result_dir (str): Directory where to save the drawn map.
    """
    res_image = Image.open(cpaths.esslingen_map)
    draw = ImageDraw.Draw(res_image)

    # start position
    x_start_pos, y_start_pos = GPSVisualizer.scale_to_img(
        Position.microdeg_to_dd(vehicle_trace.original_trace.positions[0].latitude),
        Position.microdeg_to_dd(vehicle_trace.original_trace.positions[0].longitude),
        res_image.size[0], res_image.size[1])
    draw.text((x_start_pos + 15, y_start_pos), 'Start', fill=(0, 0, 0, 255))

    # original trace
    orig_trace_image_points = [GPSVisualizer.scale_to_img(Position.microdeg_to_dd(pos.latitude),
                                                          Position.microdeg_to_dd(pos.longitude),
                                                          res_image.size[0], res_image.size[1])
                               for pos in vehicle_trace.original_trace.positions]

    draw.line(orig_trace_image_points, fill=(0, 0, 255), width=4)

    # reconstructed trace plot of the target route until it is lost e.g. after a pseudo change
    reconstructed_trace_image_points = []
    for pos in vehicle_trace.reconstructed_traces[0].positions:
        x1, y1 = GPSVisualizer.scale_to_img(Position.microdeg_to_dd(pos.latitude),
                                            Position.microdeg_to_dd(pos.longitude), res_image.size[0],
                                            res_image.size[1])
        reconstructed_trace_image_points.append((x1, y1))
    draw.line(reconstructed_trace_image_points, fill=(255, 0, 0), width=1)

    # Draw legend
    draw.rectangle((5, 5, 130, 35), fill='#d3d3d3', outline='black')
    draw.text((10, 10), 'Original route', fill=(0, 0, 255, 255))
    draw.text((10, 20), 'Reconstructed route', fill=(255, 0, 0, 255))

    # plot the positions of the other vehicles at t=target lost
    vehicle_pos_target_lost = list()
    t_target_lost = vehicle_trace.reconstructed_traces[0].positions[-1].timestamp
    for vehicle_pos in vehicle_traces:
        # search positions for t = target lost
        for pos in vehicle_pos.original_trace.positions:
            if pos.timestamp == t_target_lost:
                vehicle_pos_target_lost.append((vehicle_pos.static_id, pos.longitude, pos.latitude))

    for pos in vehicle_pos_target_lost:
        x1, y1 = GPSVisualizer.scale_to_img(Position.microdeg_to_dd(pos[2]), Position.microdeg_to_dd(pos[1]),
                                            res_image.size[0], res_image.size[1])
        draw.text((x1, y1), str(pos[0]), fill=(128, 128, 128, 255))

    vehicle_trace_map = os.path.join(result_dir, f'map_{vehicle_trace.static_id}.png')
    res_image.save(vehicle_trace_map)
    res_image.close()


def draw_overview_map(scenario_esslingen_map: str, vehicle_traces: 'list[VehicleTrace]'):
    """Draws an overview map of the routes of all vehicles onto a static map.

    Args:
        scenario_esslingen_map (str): Path to static esslingen map.
        vehicle_traces (list[VehicleTrace]): Routes and traces of all vehicles.
    """
    res_image_all = Image.open(scenario_esslingen_map)
    draw_all = ImageDraw.Draw(res_image_all)

    for vehicle_trace in vehicle_traces:
        # add original route
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        orig_trace_image_points = [GPSVisualizer.scale_to_img(Position.microdeg_to_dd(pos.latitude),
                                                              Position.microdeg_to_dd(pos.longitude),
                                                              res_image_all.size[0], res_image_all.size[1])
                                   for pos in vehicle_trace.original_trace.positions]

        # start position
        x_start_pos, y_start_pos = GPSVisualizer.scale_to_img(
            Position.microdeg_to_dd(vehicle_trace.original_trace.positions[0].latitude),
            Position.microdeg_to_dd(vehicle_trace.original_trace.positions[0].longitude),
            res_image_all.size[0], res_image_all.size[1])

        draw_all.line(orig_trace_image_points, fill=color, width=2)
        draw_all.text((x_start_pos + 10, y_start_pos), str(vehicle_trace.static_id), fill=color)

    res_image_all.save(scenario_esslingen_map)
    res_image_all.close()


def write_success_rate(vehicle_trace: VehicleTrace, result_dir: str) -> float:
    """Writes the overall tracking success to a file.

    Args:
        vehicle_trace (VehicleTrace): Routes and traces of all vehicles.
        result_dir (str): Path to directory where to create the file.

    Returns:
        float: Overall tracing success.
    """
    # calculations
    max_tracking_duration = vehicle_trace.reconstructed_traces[0].duration
    tracking_success = max_tracking_duration / vehicle_trace.original_trace.duration

    # write calculated metrics to file
    with open(os.path.join(result_dir, f'result_{vehicle_trace.static_id}.txt'), 'w') as result_file:
        result_file.write(f'Original trace duration: {vehicle_trace.original_trace.duration} [ms]\n')
        result_file.write(f'Max tracking duration: {max_tracking_duration} [ms]\n')
        result_file.write(f'Tracking success: {tracking_success * 100:.2f} [%]\n')

    return tracking_success
