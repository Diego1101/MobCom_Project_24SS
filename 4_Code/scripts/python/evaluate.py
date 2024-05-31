#!/usr/bin/env python3

# Evaluates a simulation run by measuring the privacy

# @author  Martin Dell (WS22/23)
# @author  Kadir Özer (WS22/23)
# @date    11.02.2023

import os
from argparse import Namespace
import random
from typing import Any
import numpy as np
import shutil
import sys
import pandas as pd

import constants.paths as cpaths
from enums.FileType import FileType
from argparsers.EvaluateArgumentParser import EvaluateArgumentParser
from metrics.trace import get_vehicle_traces
from metrics.utilities import CAM, parse_cam_csv, parse_config, remove_duplicate_cam

# Imports of all addons
import metrics.static_attacker as sa
import metrics.dynamic_attacker as da
import metrics.degree_of_anonymity as doa
import metrics.pseudonym_consumption as pc


# Here are all addons defined
addons = [
    {
        'name': 'Static Attacker',
        'arg': 'evaluate_static_attacker',
        'evaluate_func': sa.evaluate,
    },
    {
        'name': 'Dynamic Attacker',
        'arg': 'evaluate_dynamic_attacker',
        'evaluate_func': da.evaluate,
    },
    {
        'name': 'Degree of Anonymity',
        'arg': 'evaluate_degree_of_anonymity',
        'evaluate_func': doa.evaluate,
    },
    {
        'name': 'Pseudonym Consumption',
        'arg': 'evaluate_pseudonym_consumption',
        'evaluate_func': pc.evaluate,
    },
]


def main(args: Namespace):
    """Main entry point of the script.

    Args:
        args (Namespace): Command line arguments.
    """

    set_seeds(args.seed)

    cam_csv = os.path.join(args.sim_dir, cpaths.cam_csv)

    if os.path.exists(cam_csv):
        print('Found CSV file containing CAMs.')
    else:
        print('No CSV file containing CAMs found!')
        sys.exit(1)

    print('Removing duplicate CAM messages in csv...')
    remove_duplicate_cam(cam_csv)

    cams = parse_cam_csv(cam_csv)
    print(f'Number of preprocessed CAMs: {len(cams)}')

    print_cam_stats(cams)

    print('Rebuilding trace with recorded CAM data...')
    if args.vehicles:
        print(f'Restricting reconstruction to only vehicles with ids {args.vehicles}.')
    elif args.max_vehicles:
        print(f'Restricting reconstruction to only {args.max_vehicles} vehicles.')

    traces = get_vehicle_traces(cams, args.vehicles, args.max_vehicles)

    print(f'Found {len(traces)} traces.')

    print('Reading simulation config...')
    config = get_config(args.sim_dir)
    print('Parsed simulation config.')

    if args.clean_evaluation:
        shutil.rmtree(os.path.join(args.sim_dir, cpaths.metrics_dirname), ignore_errors=True)
        print('Removed metrics folder.')

    args_dict = vars(args)
    for addon in addons:
        if not args_dict[addon['arg']]:
            continue

        try:
            print(f'\nEvaluating {addon["name"]}...\n')
            addon['evaluate_func'](args, cams=cams, traces=traces, config=config)
            print('Done.')
        except Exception as e:
            print(f'Failed to evaluate {addon["name"]}.', e)

    print('\nEvaluation done.')


def print_cam_stats(cams: 'list[CAM]'):
    """Prints the number of unique vehicles and pseudonyms to console.

    Args:
        cams (list[CAM]): Recorded CAMs.
    """
    df = pd.DataFrame([cam.__dict__ for cam in cams])

    n_vehicles = df.groupby(['static_id']).ngroups
    print(f'Number of unique vehicles: {n_vehicles}')

    n_pseudo = df.groupby(['pseudo_id']).ngroups
    print(f'Number of unique pseudonyms: {n_pseudo}')


def get_config(sim_dir: str) -> 'dict[str, Any]':
    """Returns the simulation configuration as a dictionary.

    Args:
        sim_dir (str): The path to the simulation directory containing the configuration.

    Raises:
        Exception: Configuration file does not exist in simulation directory.

    Returns:
        dict[str, Any]: Configuration of provided simulation.
    """
    cfg_file_name = cpaths.scenario_filenames[FileType.GLOBAL_CONFIG]
    cfg_path = os.path.join(sim_dir, cfg_file_name)

    if not os.path.exists(cfg_path):
        raise Exception(f'Missing {cfg_file_name} file in simulation directory.')

    return parse_config(cfg_path)


def set_seeds(seed: int):
    """Initialize the random number generators.

    Args:
        seed (int): Seed with which to initialize the random number generators.
    """
    random.seed(seed)
    np.random.seed(seed)


if __name__ == '__main__':
    parser = EvaluateArgumentParser()
    args = parser.parse_args()
    main(args)
