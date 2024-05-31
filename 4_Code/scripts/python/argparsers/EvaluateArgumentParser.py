# Argument Parser with specific arguments for the evaluate.py script

# @author  Martin Dell (WS22/23)
# @date    23.11.2022

from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path
from typing import Any


class EvaluateArgumentParser(ArgumentParser):
    """Argument parser for evaluation script.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.description = 'Evaluates a simulation run by measuring the privacy.'
        self.add_argument('--version', action='version', version='MobCom WS22/23')

        self.__add_arguments()

    def __add_arguments(self):
        self.add_argument(
            'sim_dir',
            type=self.__is_dir,
            help='Path to the result directory of the simulation run to evaluate.',
            metavar='DIRECTORY'
        )

        self.add_argument(
            '--clean',
            dest='clean_evaluation',
            action='store_true',
            help='Clears the metrics folder in the simulation result directory.'
        )

        self.add_argument(
            '--jobs', '-j',
            dest='n_jobs',
            type=int,
            default=-1,
            help=('The maximum number of concurrently running jobs, such as the number of Python worker processes. '
                  'If -1 all CPUs are used. If 1 is given, no parallel computing code is used at all, which is useful for debugging. '
                  'For jobs below -1, (n_cpus + 1 + n_jobs) are used. Thus for n_jobs = -2, all CPUs but one are used. '
                  '(Default: %(default)s)'),
            metavar='JOBS'
        )

        self.add_argument(
            '--seed',
            dest='seed',
            type=int,
            default=3,
            help='The seed to initialize the random number generators. (Default: %(default)s)'
        )

        self.add_argument(
            '--eval-static', '-s',
            dest='evaluate_static_attacker',
            action='store_true',
            help='Evaluate privacy metrics based on static attacker model.'
        )

        self.add_argument(
            '--eval-dynamic', '-d',
            dest='evaluate_dynamic_attacker',
            action='store_true',
            help='Evaluate privacy metrics based on dynamic attacker model.'
        )

        self.add_argument(
            '--eval-anonymity', '-a',
            dest='evaluate_degree_of_anonymity',
            action='store_true',
            help='Evaluate degree of anonymity privacy metrics.'
        )

        self.add_argument(
            '--eval-consumption', '-c',
            dest='evaluate_pseudonym_consumption',
            action='store_true',
            help='Evaluate pseudonym consumption privacy metrics.'
        )

        sa_group = self.add_argument_group('Static attacker options')

        sa_exclusive = sa_group.add_mutually_exclusive_group()

        sa_exclusive.add_argument(
            '--max-vehicles', '-n',
            dest='max_vehicles',
            type=self._pos_int,
            default=None,
            help='Limit the number of vehicles to evaluate. (Default: Evaluate all vehicles)'
        )

        sa_exclusive.add_argument(
            '--vehicles', '-v',
            dest='vehicles',
            type=int,
            nargs='+',
            default=None,
            help='Analyses only the vehicles identified by their service ID.',
            metavar='ID'
        )

        sa_group.add_argument(
            '--create-interactive-map', '-m',
            dest='create_interactive_map',
            action='store_true',
            help=('Additionally create an interactive map for every vehicle to visualize '
                  'the vehicles routes and reconstructed traces. '
                  '(Default: Only create interactive overview map.)')
        )

        group = self.add_argument_group('Degree of anonymity options')

        group.add_argument(
            '--cam-purge-threshold',
            dest='anonymity_cam_purge_threshold',
            type=self._pos_int,
            default=60000,
            help='Time in ms after which the cams are removed from the anonymity set of analyzed cams. (Default: %(default)sms)',
            metavar='MILLISECONDS'
        )

        group.add_argument(
            '--plot-anonymity', '-pa',
            dest='create_plots',
            action='store_true',
            help='Create and save plots of anonymity metric.'
        )

    def __is_dir(self, path: Any) -> Path:
        if not Path(path).is_dir():
            raise ArgumentTypeError(f'{path} is not a directory.')

        return path

    def _pos_int(self, value: Any) -> int:
        """Checks if `value` is a positive non-zero integer.

        Args:
            value (Any): Value to check.

        Raises:
            ArgumentTypeError: Value is not a positive non-zero integer.

        Returns:
            int: Positive non-zero integer.
        """
        value = int(value)
        if value <= 0:
            raise ArgumentTypeError(f'{value} is not a positive non-zero integer value.')

        return value
