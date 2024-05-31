# Argument Parser with specific arguments for the run.py script

# @author  Annette Grueber (WS21/22)
# @author  Martin Dell (WS22/23)
# @author  Janis Latus (WS22/23)
# @date    27.12.2022

from argparse import ArgumentParser, ArgumentTypeError
from typing import Any

import constants.arguments as args
from enums.HardwareType import HardwareType
from enums.PseudoChangeType import PseudoChangeType
from enums.ScenarioType import ScenarioType
from enums.StrategyType import StrategyType


class RunnerArgumentParser(ArgumentParser):
    """Argument parser for run simulation script.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.description = 'Starts a simulation run to measure privacy of different pseudonym change strategies.'
        self.add_argument('--version', action='version', version='MobCom WS22/23')

        self._add_arguments()

    def _add_arguments(self):
        # Add argument for the scenario
        self.add_argument(
            *args.scenario['arg'],
            **self._kwargs(args.scenario),
            type=ScenarioType,
            choices=list(ScenarioType),
        )

        # Add argument for the vehicle spawn rate
        self.add_argument(
            *args.spawn_rate['arg'],
            **self._kwargs(args.spawn_rate),
            type=self._pos_float,
        )

        # Add argument if sumo or sumo-gui start as a server
        self.add_argument(
            *args.no_sumo_gui['arg'],
            **self._kwargs(args.no_sumo_gui),
            action='store_true',
        )

        # Add argument if the tip info should be logged out or not.
        self.add_argument(
            *args.no_logging['arg'],
            **self._kwargs(args.no_logging),
            action='store_true',
        )

        self.add_argument(
            *args.strategy['arg'],
            **self._kwargs(args.strategy),
            type=StrategyType,
            choices=list(StrategyType),
        )

        self.add_argument(
            *args.pseudonym_change['arg'],
            **self._kwargs(args.pseudonym_change),
            type=PseudoChangeType,
            choices=list(PseudoChangeType),
        )

        self.add_argument(
            *args.sim_time['arg'],
            **self._kwargs(args.sim_time),
            type=self._pos_float,
        )

        self.add_argument(
            *args.seed['arg'],
            **self._kwargs(args.seed),
            type=int,
        )

        self.add_argument(
            *args.jobs['arg'],
            **self._kwargs(args.jobs),
            type=int,
        )

        self.add_argument(
            *args.only_generation['arg'],
            **self._kwargs(args.only_generation),
            action='store_true',
        )

        self.add_argument(
            *args.dry_run['arg'],
            **self._kwargs(args.dry_run),
            action='store_true',
        )

        self.add_argument(
            *args.simulate_scenario['arg'],
            **self._kwargs(args.simulate_scenario),
            type=str,
        )

        self._add_dynamic_attacker_arguments()
        self._add_pcs_periodical_arguments()
        self._add_pcs_distance_arguments()
        self._add_pcs_slow_arguments()
        self._add_pcs_whisper_arguments()
        self._add_pcs_cpn_arguments()
        self._add_hw_arguments()

    def _add_dynamic_attacker_arguments(self):
        group = self.add_argument_group('Dynamic Attacker', 'Arguments controlling the dynamic attacker')

        exclusive = group.add_mutually_exclusive_group()

        exclusive.add_argument(
            *args.attacker_id['arg'],
            **self._kwargs(args.attacker_id),
            type=str,
        )

        exclusive.add_argument(
            *args.spawn_delay['arg'],
            **self._kwargs(args.spawn_delay),
            type=self._pos_float,
        )

        group.add_argument(
            *args.target_id['arg'],
            **self._kwargs(args.target_id),
            type=str,
        )

        group.add_argument(
            *args.visual_range['arg'],
            **self._kwargs(args.visual_range),
            type=self._pos_float,
        )

    def _add_pcs_periodical_arguments(self):
        group = self.add_argument_group('PCS Periodical', 'Arguments controlling \'Periodical\' pseudonym change strategy')

        group.add_argument(
            *args.pseudonym_lifetime['arg'],
            **self._kwargs(args.pseudonym_lifetime),
            type=self._pos_float,
        )

    def _add_pcs_distance_arguments(self):
        group = self.add_argument_group('PCS Distance', 'Arguments controlling \'Distance\' pseudonym change strategy')

        group.add_argument(
            *args.distance_threshold['arg'],
            **self._kwargs(args.distance_threshold),
            type=self._pos_float,
        )

    def _add_pcs_slow_arguments(self):
        group = self.add_argument_group('PCS SLOW', 'Arguments controlling \'SLOW\' pseudonym change strategy')

        group.add_argument(
            *args.slow_threshold['arg'],
            **self._kwargs(args.slow_threshold),
            type=self._pos_float,
        )

    def _add_pcs_whisper_arguments(self):
        group = self.add_argument_group('PCS WHISPER', 'Arguments controlling \'WHISPER\' pseudonym change strategy')

        group.add_argument(
            *args.whisper_road_neighbor_radius['arg'],
            **self._kwargs(args.whisper_road_neighbor_radius),
            type=self._pos_float,
        )

        group.add_argument(
            *args.whisper_general_neighbor_radius['arg'],
            **self._kwargs(args.whisper_general_neighbor_radius),
            type=self._pos_float,
        )

        group.add_argument(
            *args.whisper_close_neighbor_radius['arg'],
            **self._kwargs(args.whisper_close_neighbor_radius),
            type=self._pos_float,
        )

        group.add_argument(
            *args.whisper_counter['arg'],
            **self._kwargs(args.whisper_counter),
            type=self._pos_int,
        )

    def _add_pcs_cpn_arguments(self):
        group = self.add_argument_group('PCS CPN', 'Arguments controlling \'CPN\' pseudonym change strategy')

        group.add_argument(
            *args.cpn_neighbor_threshold['arg'],
            **self._kwargs(args.cpn_neighbor_threshold),
            type=self._pos_int,
        )

        group.add_argument(
            *args.cpn_neighbor_radius['arg'],
            **self._kwargs(args.cpn_neighbor_radius),
            type=self._pos_float,
        )

    def _add_hw_arguments(self):
        group = self.add_argument_group('Hardware', 'Arguments controlling hardware integration')

        group.add_argument(
            *args.hardware['arg'],
            **self._kwargs(args.hardware),
            type=HardwareType,
            choices=list(HardwareType),
        )

        group.add_argument(
            *args.hardware_veh_id['arg'],
            **self._kwargs(args.hardware_veh_id),
            type=str,
        )
        group.add_argument(
            *args.hardware_local_ip['arg'],
            **self._kwargs(args.hardware_local_ip),
            type=str,
        )

        group.add_argument(
            *args.hardware_local_port['arg'],
            **self._kwargs(args.hardware_local_port),
            type=int,
        )

        group.add_argument(
            *args.hardware_remote_ip['arg'],
            **self._kwargs(args.hardware_remote_ip),
            type=str,
        )

        group.add_argument(
            *args.hardware_remote_port['arg'],
            **self._kwargs(args.hardware_remote_port),
            type=int,
        )

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

    def _pos_float(self, value: Any) -> float:
        """Checks if `value` is a positive non-zero float.

        Args:
            value (Any): Value to check.

        Raises:
            ArgumentTypeError: Value is not a positive non-zero float.

        Returns:
            int: Positive non-zero float.
        """
        value = float(value)
        if value <= 0:
            raise ArgumentTypeError(f'{value} is not a positive non-zero float value.')

        return value

    def _kwargs(self, arg):
        """Converts an argument dict to keywords arguments for `add_argument`.
        """
        kwargs = {
            'dest': arg['key'],
            'help': arg['help'],
        }

        if 'default' in arg:
            kwargs['default'] = arg['default']

        if 'metavar' in arg:
            kwargs['metavar'] = arg['metavar']

        return kwargs
