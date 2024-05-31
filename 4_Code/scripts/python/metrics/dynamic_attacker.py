# Evaluates the dynamic attacker by visualizing the target and attacker routes.
# @author  Martin Dell (WS22/23)
# @author  Kadir Özer (WS22/23)
# @date    07.02.2023

import os
from argparse import Namespace

import pandas as pd
import constants.paths as cpaths
from matplotlib import pyplot as plt
from enums.FileType import FileType
from metrics.utilities import parse_config

POINT_SIZE = 10  # Size of a location point in the plot


def evaluate(args: Namespace, **kwargs):
    """Evaluates the dynamic attacker in the simulation run.

    Args:
        args (Namespace): Evaluation options.

    Raises:
        Exception: Simulation not run with dynamic attacker enabled.
    """
    # Reading csv
    result_dynamic_att_file_path = os.path.join(args.sim_dir, cpaths.dynamic_attacker_csv)
    result_vehicle_file_path = os.path.join(args.sim_dir, cpaths.vehicles_csv)
    # Getting the target ID, so we know which car to look for in the vehicles.csv
    target_id = get_target_id(args)

    if not os.path.exists(result_dynamic_att_file_path):
        raise Exception(
            f'Simulation was not run with dynamic attacker or required file {cpaths.dynamic_attacker_csv} is missing.')
    elif not os.path.exists(result_vehicle_file_path):
        raise Exception(f'Required file {cpaths.vehicles_csv} is missing.')

    dyn_att_df = pd.read_csv(result_dynamic_att_file_path, squeeze=True,
                             dtype={'TargetVisible': bool, 'CorrectVehicle': bool})

    target_df = pd.read_csv(result_vehicle_file_path, squeeze=True)

    # Drop duplicate values in dynamic_attacker.csv file
    dyn_att_df = dyn_att_df.drop_duplicates()

    # Convert all coordinate columns to decimal degree representation
    coord_col = ['AttackerLongitude', 'AttackerLatitude']
    dyn_att_df[coord_col] = dyn_att_df[coord_col].div(1E7)

    coord_col_target = ['Longitude', 'Latitude']
    target_df[coord_col_target] = target_df[coord_col_target].div(1E7)

    # Filter location data of attacker based on his tracking style: Visual or with CAM
    attacker_visual = dyn_att_df.loc[dyn_att_df['TargetVisible'], ['AttackerLongitude', 'AttackerLatitude']]
    attacker_cam = dyn_att_df.loc[~dyn_att_df['TargetVisible'], ['AttackerLongitude', 'AttackerLatitude']]
    # Filter location data of vehicles.csv based on target_id
    target_route = target_df[target_df['SumoID'] == target_id]

    x_target = target_route['Longitude']
    y_target = target_route['Latitude']

    x_attacker_visual = attacker_visual['AttackerLongitude']
    y_attacker_visual = attacker_visual['AttackerLatitude']

    x_attacker_cam = attacker_cam['AttackerLongitude']
    y_attacker_cam = attacker_cam['AttackerLatitude']

    # Getting the last timestamp from the dynamic_attacker.csv to see where he lost his target
    last_attacker_timestamp = dyn_att_df['Timestamp'].max()
    # create the missed route of the attacker
    target_remain = target_route[target_route['Timestamp'] > last_attacker_timestamp]

    x_target_remain = target_remain['Longitude']
    y_target_remain = target_remain['Latitude']
    # saves the first coordinates at which the pseudonym changes and the pseudonym itself
    pseudonym_changes = target_route.groupby(['Pseudonym'])[['Longitude', 'Latitude']].first()

    fig, ax = plt.subplots(3, sharex=True, sharey=True)
    fig.set_size_inches(8, 10.5)

    # Functions for plotting the three different graphs
    plot_target_route(ax[0], x_target, y_target, x_target_remain, y_target_remain)
    plot_attacker_route(ax[1], x_attacker_visual, y_attacker_visual, x_attacker_cam, y_attacker_cam)
    plot_overlapped_route(ax[2], x_target, y_target,
                          x_attacker_visual, y_attacker_visual,
                          x_attacker_cam, y_attacker_cam, pseudonym_changes)

    # Save results
    result_dir = os.path.join(args.sim_dir, cpaths.metrics_dirname, cpaths.dynamic_attacker_dirname)
    os.makedirs(result_dir, exist_ok=True)

    fig.tight_layout()
    fig.savefig(os.path.join(result_dir, cpaths.dynamic_attacker_dirname), dpi=200)

# Function for plotting the route of the target from the vehicles.csv file and also
# for plotting the part of the targets route if the attacker missed any
def plot_target_route(ax: plt.Axes, xtarget, ytarget, x_target_remain, y_target_remain):
    ax.scatter(xtarget, ytarget, s=POINT_SIZE, color='grey', label='Target Route')
    ax.annotate('Start', (xtarget.iloc[0], ytarget.iloc[0]), xytext=(-10, -10), textcoords='offset points', color='black')

    if len(x_target_remain) > 0:
        ax.scatter(x_target_remain, y_target_remain, s=POINT_SIZE, color='darkorange', label='Missed Target Route')

    ax.set_title('Target Route')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.legend()
    ax.ticklabel_format(useOffset=False)

# Function for plotting the attackers route
def plot_attacker_route(ax: plt.Axes, xvisual, yvisual, xcam, ycam):
    ax.scatter(xvisual, yvisual, s=POINT_SIZE, color='blue', label='Following visually')
    ax.scatter(xcam, ycam, s=POINT_SIZE, color='red', label='Following with CAM')
    ax.set_title('Attacker Route')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.legend(loc='upper left')
    ax.ticklabel_format(useOffset=False)

# Function for plotting the pseudonym changes into the diagrams
def plot_pseudonym_changes(ax: plt.Axes, pseudonym_changes):
    ax.scatter(pseudonym_changes['Longitude'], pseudonym_changes['Latitude'],
               c='black', marker='*', label='Pseudonym Change')

    for pseudonym, pos in pseudonym_changes.iterrows():
        ax.annotate(pseudonym, (pos['Longitude'], pos['Latitude']), xytext=(2, -14),
                    textcoords='offset points', color='black')

# Function for plotting both routes and the pseudonym changes into one plot
def plot_overlapped_route(ax: plt.Axes, xtarget, ytarget, xvisual, yvisual, xcam, ycam, pseudonym_changes):
    plot_attacker_route(ax, xvisual, yvisual, xcam, ycam)
    ax.plot(xtarget, ytarget, 'k', alpha=0.2, linewidth=8, label='Target Route')
    plot_pseudonym_changes(ax, pseudonym_changes)

    ax.set_title('Overlap')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.legend()
    ax.ticklabel_format(useOffset=False)

# Function for getting the target ID out of the attacker_info.yml file
def get_target_id(args):
    cfg_file_name = cpaths.scenario_filenames[FileType.ATTACKER_INFO]
    cfg_path = os.path.join(args.sim_dir, cfg_file_name)

    info = parse_config(cfg_path)

    target_sumo_id = info['target_id']

    return target_sumo_id
