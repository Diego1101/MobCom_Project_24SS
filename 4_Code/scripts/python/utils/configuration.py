# Configuration wrapper for argument and GUI settings

# @author  Martin Dell (WS22/23)
# @author  Janis Latus (WS22/23)
# @date    27.12.2022


from enum import Enum
from typing import Any, Optional

import constants.arguments as args
import yaml
from enums.HardwareType import HardwareType
from enums.PseudoChangeType import PseudoChangeType
from enums.ScenarioType import ScenarioType
from enums.StrategyType import StrategyType


class EnumDumper(yaml.Dumper):
    """Represent enums by their string value.
    """
    def represent_data(self, data):
        if isinstance(data, Enum):
            return self.represent_data(data.value)

        return super().represent_data(data)


class Config:
    """Wrapper for argument namespace serving as a config.
    """
    def __init__(self, arguments: 'dict[str, Any]'):
        self._cfg = arguments

    def __getitem__(self, key: str) -> Any:
        return self._cfg[key]

    def __setitem__(self, key: str, new_value: Any) -> None:
        self._cfg[key] = new_value

    def __contains__(self, key: str) -> bool:
        return key in self._cfg

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return yaml.dump(self._cfg, Dumper=EnumDumper, default_flow_style=False)

    def _get_prop(self, key: str):
        return self.__getitem__(key)

    def items(self):
        return self._cfg.items()

    def dict(self) -> 'dict[str, Any]':
        """Returns configuration as dictionary.

        Returns:
            dict[str, Any]: Configuration.
        """
        return self._cfg

    def dump(self, file_path: str):
        """Writes the used config options (arguments) to run the simulation scenario to a file.

        Args:
            file_path (str): Path of the file to write to.
        """

        with open(file_path, 'w') as f:
            yaml.dump(self._cfg, f, Dumper=EnumDumper, default_flow_style=False)


class PseudoConfig(Config):
    """Config for pseudonym change strategies.
    """
    @property
    def strategy(self) -> PseudoChangeType:
        return self._get_prop(args.pseudonym_change['key'])

    @property
    def lifetime(self) -> float:
        return self._get_prop(args.pseudonym_lifetime['key'])

    @property
    def distance_threshold(self) -> int:
        return self._get_prop(args.distance_threshold['key'])

    @property
    def slow_threshold(self) -> int:
        return self._get_prop(args.slow_threshold['key'])

    @property
    def whisper_general_neighbor_radius(self) -> float:
        return self._get_prop(args.whisper_general_neighbor_radius['key'])

    @property
    def whisper_road_neighbor_radius(self) -> float:
        return self._get_prop(args.whisper_road_neighbor_radius['key'])

    @property
    def whisper_close_neighbor_radius(self) -> float:
        return self._get_prop(args.whisper_close_neighbor_radius['key'])

    @property
    def whisper_counter(self) -> int:
        return self._get_prop(args.whisper_counter['key'])

    @property
    def cpn_neighbor_radius(self) -> float:
        return self._get_prop(args.cpn_neighbor_radius['key'])

    @property
    def cpn_neighbor_threshold(self) -> int:
        return self._get_prop(args.cpn_neighbor_threshold['key'])


class AttackerConfig(Config):
    """Config for the attacker profile.
    """
    @property
    def strategy(self) -> StrategyType:
        return self._get_prop(args.strategy['key'])

    @property
    def attacker_id(self) -> str:
        return self._get_prop(args.attacker_id['key'])

    @attacker_id.setter
    def attacker_id(self, id: str) -> Optional[str]:
        self[args.attacker_id['key']] = id

    @property
    def spawn_delay(self) -> float:
        return self._get_prop(args.spawn_delay['key'])

    @property
    def target_id(self) -> Optional[str]:
        return self._get_prop(args.target_id['key'])

    @target_id.setter
    def target_id(self, id: str):
        self[args.target_id['key']] = id

    @property
    def visual_range(self) -> float:
        return self._get_prop(args.visual_range['key'])

    def dump_attacker_info(self, file_path: str):
        """Writes the current attacker and target id to a file.

        Args:
            file_path (str): Path of the file to write to.
        """
        info = {
            args.attacker_id['key']: self.attacker_id,
            args.target_id['key']: self.target_id,
        }

        with open(file_path, 'w') as f:
            yaml.dump(info, f, default_flow_style=False)


class HardwareConfig(Config):
    """Config for hardware integration.
    """
    @property
    def type(self) -> HardwareType:
        return self._get_prop(args.hardware['key'])

    @property
    def hardware_veh_id(self) -> Optional[str]:
        return self._get_prop(args.hardware_veh_id['key'])

    @property
    def local_ip(self) -> str:
        return self._get_prop(args.hardware_local_ip['key'])

    @property
    def remote_ip(self) -> str:
        return self._get_prop(args.hardware_remote_ip['key'])

    @property
    def local_port(self) -> int:
        return self._get_prop(args.hardware_local_port['key'])

    @property
    def remote_port(self) -> int:
        return self._get_prop(args.hardware_remote_port['key'])


class SimConfig(Config):
    """Config for the complete simulation.
    """
    def __init__(self, arguments: 'dict[str, Any]'):
        super().__init__(arguments)

        self.hardware_config = HardwareConfig(arguments)
        self.attacker_config = AttackerConfig(arguments)
        self.pseudo_config = PseudoConfig(arguments)

    @property
    def hardware(self) -> HardwareConfig:
        return self.hardware_config

    @property
    def attacker(self) -> AttackerConfig:
        return self.attacker_config

    @property
    def pcs(self) -> PseudoConfig:
        return self.pseudo_config

    @property
    def scenario(self) -> ScenarioType:
        return self._get_prop(args.scenario['key'])

    @property
    def spawn_rate(self) -> float:
        return self._get_prop(args.spawn_rate['key'])

    @property
    def no_sumo_gui(self) -> bool:
        return self._get_prop(args.no_sumo_gui['key'])

    @property
    def no_logging(self) -> bool:
        return self._get_prop(args.no_logging['key'])

    @property
    def simulate_scenario(self) -> Optional[str]:
        return self._get_prop(args.simulate_scenario['key'])

    @property
    def sim_time(self) -> float:
        return self._get_prop(args.sim_time['key'])

    @property
    def seed(self) -> int:
        return self._get_prop(args.seed['key'])

    @property
    def n_jobs(self) -> int:
        return self._get_prop(args.jobs['key'])

    @property
    def run_only_generation(self) -> bool:
        return self._get_prop(args.only_generation['key'])

    @property
    def is_dry_run(self) -> bool:
        return self._get_prop(args.dry_run['key'])
