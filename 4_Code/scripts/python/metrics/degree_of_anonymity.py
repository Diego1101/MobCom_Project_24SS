# File implements the analysis of a simulation by
# applying the effective anonymity set size (eass) and
# the degree of anonymity.

# @author  Nik Steinbrügge (WS22/23)
# @author  Martin Dell (WS22/23)
# @date    29.11.2022

import math
import os
from argparse import Namespace

import constants.paths as cpaths
import matplotlib.pyplot as plt

from matplotlib.ticker import MaxNLocator
from metrics.utilities import CAM


def evaluate(args: Namespace, cams: 'list[CAM]', **kwargs) -> float:
    """Evaluates the degree of anonymity privacy metric.

    Args:
        args (Namespace): Evaluation options.
        cams (list[CAM]): Preprocessed cam messages.

    Returns:
        float: Degree of anonymity (normalized [0,1]). Higher is better.
    """

    anonymity_set = calculate_anonymity_set(cams, args.anonymity_cam_purge_threshold)
    print(f'Size of anonymity set: {len(anonymity_set)}')

    eass = calculate_entropy_and_eass(anonymity_set)
    print(f'Effective anonymity set size: {eass:.4f}')

    degree_of_anon = calculate_degree_of_anonymity(anonymity_set, eass)
    print(f'Degree of anonymity: {degree_of_anon:.4f}')

    metric_dir = os.path.join(args.sim_dir, cpaths.metrics_dirname, cpaths.anonymity_dirname)
    os.makedirs(metric_dir, exist_ok=True)

    if args.create_plots:
        print('\nPlotting results...')

        # functions to create some plot to visualize data
        plot_cams_over_time(cams, metric_dir)
        plot_anonymity_set(anonymity_set, metric_dir)

        print('Plotting done.')

    with open(os.path.join(metric_dir, 'degree_of_anonymity.txt'), 'w') as f:
        f.write(f'Degree of anonymity: {degree_of_anon:.4f}')

    return degree_of_anon


def calculate_anonymity_set(cams: 'list[CAM]', cam_anonymity_set_purge_threshold: int, end_timestamp: int = 0) -> 'dict[int, tuple[int, int]]':
    """Calculates the anonymity set.

    Args:
        cams (list[CAM]): List of all send cam messages.
        cam_anonymity_set_purge_threshold (int): Time in ms after which the cams are removed from the anonymity set of analyzed CAMS.
        end_timestamp (int, optional): Timestamp where to stop considering new cam messages. Defaults to 0.

    Returns:
        dict[int, tuple[int, int]]: Anonymity set. Key is pseudonym ID, value is a tuple of (number of msg received, time of last message received)
    """

    # dict with
    # key = pseudo_id
    # value (number of msg received, time of last message received)
    anonymity_set: dict[int, tuple[int, int]] = {}

    # timestamp at what last time the set was purged of outdated messages
    last_purge_timestamp = 0

    for cam in cams:
        # if defined end time is reached, break and return
        if end_timestamp != 0 and cam.timestamp >= end_timestamp:
            break

        # count number of cams received, categorized by pseud_ids
        # pseud_id already in set
        if cam.pseudo_id in anonymity_set:
            # add
            anonymity_set[cam.pseudo_id] = (anonymity_set[cam.pseudo_id][0] + 1, cam.timestamp)
        else:
            # Add new element to set
            anonymity_set[cam.pseudo_id] = (1, cam.timestamp)

        # purge set of outdated messages
        # if last purge already happened at timestamp, skip purge
        if last_purge_timestamp == cam.timestamp:
            continue

        lst_of_to_be_purged_keys: list[int] = []
        for (pseudo_id, (_, time_when_last_msg_received)) in anonymity_set.items():
            if (cam.timestamp - time_when_last_msg_received) > cam_anonymity_set_purge_threshold:
                lst_of_to_be_purged_keys.append(pseudo_id)

        for pseudo_id in lst_of_to_be_purged_keys:
            anonymity_set.pop(pseudo_id)

        last_purge_timestamp = cam.timestamp

    return anonymity_set


def calculate_entropy_and_eass(anonymity_set: 'dict[int, tuple[int, int]]') -> float:
    """Calculate the effective anonymity set size as precalculation for the Degree of Anonymity.

    Args:
        anonymity_set (dict[int, tuple[int, int]]): Dictionary where key is the pseudonym and
            the value is a tuple of the number of CAMs received and the time of last CAM received.

    Returns:
        float: Effective Anonymity Set Size (which is the entropy of given anonymity set).
    """
    # count number of cams in anonymity set
    n_total_cams = 0.0
    for (n_pseudo_cams, _) in anonymity_set.values():
        n_total_cams += n_pseudo_cams

    # dict with pseudo_id as key and its probability as value
    # probability = (number of cams of this pseudo_id) / (absolute number of cams)
    pseudo_prob_dict: dict[int, float] = {}
    for (key, (n_pseudo_cams, _)) in anonymity_set.items():
        pseudo_prob_dict[key] = n_pseudo_cams / n_total_cams

    # calculate entropy
    entropy_tmp = 0.0
    for prob in pseudo_prob_dict.values():
        # logarithm of base 2
        entropy_tmp += prob * math.log(prob, 2)

    # negate to finish entropy calculation
    eass = -entropy_tmp

    return eass


def calculate_degree_of_anonymity(anonymity_set: 'dict[int, tuple[int, int]]', eass: float) -> float:
    """Calculate the Degree of Anonymity.

    Args:
        anonymity_set (dict[int, tuple[int, int]]): Dictionary where key is the pseudonym and
            the value is a tuple of the number of CAMs received and the time of last CAM received.
        eass (float): Effective anonymity set size

    Returns:
        float: Degree of Anonymity (which is the normalized EASS).
    """
    # special case, division by 0, if anonymity set has only 1 element
    if len(anonymity_set) <= 1:
        print('\033[91mDegree of anonymity can\'t be calculated. Anonymity Set is <= 1. \033[0m')
        return -1

    # degree of anonymity = eass / max_entropy

    # calculate max possbile entropy of the anonymity set for calculating the degree of anonymity
    max_possible_entropy = math.log(len(anonymity_set), 2)

    degree_of_anon = eass / max_possible_entropy

    return degree_of_anon


def plot_cams_over_time(cams: 'list[CAM]', out_dir: str):
    # plot a histogram of the course of absolute number of received cams over time
    # just for visualizing purposes

    # get max time value of a cam message
    max_timestamp = cams[-1].timestamp
    x_axis = range(max_timestamp + 1)

    # parse y axis
    lst = [0] * (max_timestamp + 1)

    for cam_msg_count, cam in enumerate(cams):
        lst[cam.timestamp] = cam_msg_count + 1

    # fill time slots where no cam is received, to show the absolute number
    # of received cams over time
    for i in range(1, len(lst)):
        if lst[i] == 0:
            lst[i] = lst[i - 1]

    plt.plot(x_axis, lst)
    plt.title('Absolute number of CAMs received over time')
    plt.ylabel('Number of CAMs received')
    plt.xlabel('time')

    plt.savefig(os.path.join(out_dir, 'cams_over_time_plot.png'))


def plot_anonymity_set(anonymity_set: 'dict[int, tuple[int, int]]', out_dir: str):
    # plot the anonymity set as bar graph
    # for visualizing purposes
    pseudo_ids = [str(pseudo_id) for pseudo_id in anonymity_set.keys()]
    number_of_msgs = [n_pseudo_cams for (n_pseudo_cams, _) in anonymity_set.values()]

    # plot
    _, ax = plt.subplots(figsize=(20, 12))
    ax.bar(pseudo_ids, number_of_msgs, width=0.7)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    plt.title('Anonymity Set')
    plt.ylabel('Number of CAMs received')
    plt.xlabel('Pseudonyms')
    # rotate x-axis labels to be readable, but they are too big and hang out of the image
    plt.xticks(rotation=90)

    plt.savefig(os.path.join(out_dir, 'anonymity_set_plot.png'))
