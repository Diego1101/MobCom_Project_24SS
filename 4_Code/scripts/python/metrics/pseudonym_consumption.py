# File implements calculation of pseudonym consumption metric

# @author Nik Steinbrügge (WS22/23)
# @author Martin Dell (WS22/23)
# @date 30.12.2022

import os
from argparse import Namespace
from csv import writer
from statistics import mean, median, stdev
from typing import Any

import constants.paths as cpaths
import matplotlib.pyplot as plt
from metrics.utilities import CAM


def evaluate(args: Namespace, cams: 'list[CAM]', config: 'dict[str, Any]', **kwargs):
    """Evaluates the pseudonym consumption privacy metrics.

    Args:
        args (Namespace): Evaluation options.
        cams (list[CAM]): List of recorded cams from all vehicles.
        config (dict[str, Any]): Simulation configuration.
    """

    # prepare directory structure
    out_dir = os.path.join(args.sim_dir, cpaths.metrics_dirname, cpaths.consumption_dirname)
    os.makedirs(out_dir, exist_ok=True)

    sim_time: float = config['sim_time']

    print(f'Total simulation time: {sim_time}s.')

    print('Calculating pseudonym consumption...')
    pseudonym_consumption = calculate_pseudonym_consumption(cams, sim_time)

    # Outputs
    write_pseudonym_consumption(out_dir, pseudonym_consumption)
    write_stats(out_dir, pseudonym_consumption)
    plot_consumption_characteristics(out_dir, pseudonym_consumption)

    print('\nWritten results to: ')
    print(out_dir)


def calculate_pseudonym_consumption(cams: 'list[CAM]', sim_time: float) -> 'dict[int, float]':
    """Calculate the pseudonym consumption per second for each vehicle (static ID).

    Args:
        cams (list[CAM]): List of recorded cams from all vehicles.
        sim_time (float): Total simulation time.

    Returns:
        dict[int, float]: Pseudonym consumption for each vehicle.
    """
    # Dict with static ids as key and set of pseudonym ids as value
    pseudonyms_per_id: dict[int, set[int]] = {}

    for cam in cams:
        # Add pseudonym to static id, or create new set if there are no pseudonyms.
        pseudonyms = pseudonyms_per_id.setdefault(cam.static_id, set())
        pseudonyms.add(cam.pseudo_id)

    # calculate pseudo consumption for each static id
    pseudonym_consumption = {
        static_id: len(pseudonyms) / sim_time
        for static_id, pseudonyms in pseudonyms_per_id.items()}

    return pseudonym_consumption


def write_pseudonym_consumption(out_dir: str, pseudonym_consumption: 'dict[int, float]'):
    """Write pseudonym consumption of each vehicle to a CSV file.

    Args:
        out_dir (str): The output directory where the CSV file will be written to.
        pseudonym_consumption (dict[int, float]): Pseudonym consumption of each vehicle.
    """
    with open(os.path.join(out_dir, cpaths.pseudonym_consumption), 'w', newline='') as f:
        csv_writer = writer(f)

        csv_writer.writerow(['Static ID', 'Pseudonym Consumption Rate'])
        # write data to file
        csv_writer.writerows((sid, f'{consumption:.4f}') for sid, consumption in pseudonym_consumption.items())


def write_stats(out_dir: str, pseudonym_consumption: 'dict[int, float]'):
    """
    Write min, max, median, mean and stdev of the pseudonym consumption
    of all vehicles to console and file.

    Args:
        out_dir (str): The output directory where the file will be written to.
        pseudonym_consumption (dict[int, float]): Pseudonym consumption of each vehicle.
    """

    # calculate characteristics
    min_pseudo_cons = min(pseudonym_consumption.values())
    max_pseudo_cons = max(pseudonym_consumption.values())
    med_pseudo_cons = median(pseudonym_consumption.values())
    mean_pseudo_cons = mean(pseudonym_consumption.values())
    std_pseudo_cons = stdev(pseudonym_consumption.values())

    print(f'{"Min:":<10}{min_pseudo_cons:.4f} Hz ({1 / min_pseudo_cons:>6.2f} sec/pseudonym)')
    print(f'{"Max:":<10}{max_pseudo_cons:.4f} Hz ({1 / max_pseudo_cons:>6.2f} sec/pseudonym)')
    print(f'{"Median:":<10}{med_pseudo_cons:.4f} Hz ({1 / med_pseudo_cons:>6.2f} sec/pseudonym)')
    print(f'{"Mean:":<10}{mean_pseudo_cons:.4f} Hz ({1 / mean_pseudo_cons:>6.2f} sec/pseudonym)')
    print(f'{"Stdev:":<10}{std_pseudo_cons:.4f} Hz ({1 / std_pseudo_cons:>6.2f} sec/pseudonym)')

    # Write to file
    with open(os.path.join(out_dir, cpaths.pseudonym_consumption_stats), 'w') as f:
        f.write(f'Min: {min_pseudo_cons:.4f} Hz\n')
        f.write(f'Max: {max_pseudo_cons:.4f} Hz\n')
        f.write(f'Median: {med_pseudo_cons:.4f} Hz\n')
        f.write(f'Mean: {mean_pseudo_cons:.4f} Hz\n')
        f.write(f'Stdev: {std_pseudo_cons:.4f} Hz\n')


def plot_consumption_characteristics(out_dir: str, pseudonym_consumption: 'dict[int, float]'):
    """Plot the overall pseudonym consumption of all vehicles.

    Args:
        out_dir (str): The output directory where the file will be written to.
        pseudonym_consumption (dict[int, float]): Pseudonym consumption of each vehicle.
    """
    # source: https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.boxplot.html
    # apparently characteristic values are auto computed by matplotlib
    # Maybe finetune or build a custom plot that represents alle the already computed values

    fig1, ax1 = plt.subplots()
    ax1.set_title('Pseudonym Consumption Rate')
    ax1.boxplot([v for v in pseudonym_consumption.values()], showmeans=True)
    ax1.set_ylabel('Pseudonym Consumption Rate (Hz)')
    ax1.get_xaxis().set_visible(False)
    plt.savefig(os.path.join(out_dir, cpaths.pseudonym_consumption_plot))
