# Python file contains all constants for the argument parser

# @author  Annette Grueber (WS21/22)
# @author  Martin Dell (WS22/23)
# @author  Janis Latus (WS22/23)
# @date    27.12.2022

from typing_extensions import TypedDict, NotRequired
from typing import Any

from enums.ScenarioType import ScenarioType
from enums.HardwareType import HardwareType
from enums.PseudoChangeType import PseudoChangeType
from enums.StrategyType import StrategyType


class Argument(TypedDict):
    """Represents a configurable simulation parameter.
    """
    arg: 'list[str]'            # Argument flags, e.g. --my-param, -mp
    key: str                    # Internal unique key to access this argument in the configuration.
    help: str                   # Description of the argument. This text is also used in the GUI as the tooltip.
    metavar: NotRequired[str]   # Optional text after "arg". Will be shown in the command line manuel when --help is passed. E.g. writing METERS will output --my-param METERS in the manuel.


class DefaultArgument(Argument):
    """Represents a configurable simulation parameter with default value.
    """
    default: Any                # Default value of the argument. Must be of the same type as the argument.


# Generic options
scenario: DefaultArgument = {
    'arg': ['--scenario', '-s'],
    'key': 'scenario',
    'default': ScenarioType.ESSLINGENEXT,
    'help': 'Selection of the map the simulation should run on. (Default: %(default)s)',
}

spawn_rate: DefaultArgument = {
    'arg': ['--spawn-rate', '-r'],
    'key': 'spawn_rate',
    'default': 3,
    'help': ('Approximate spawn rate of vehicles per minute in the simulation. '
             '(Default: %(default)s vehicles per minute)'),
}

no_sumo_gui: Argument = {
    'arg': ['--no-sumo-gui', '-ng'],
    'key': 'no_sumo_gui',
    'help': 'Start the simulation without the OMNet++ Qtenv and SUMO GUI.',
}

no_logging: Argument = {
    'arg': ['--no-logging', '-nl'],
    'key': 'no_logging',
    'help': 'Deactivate the vehicle info logging for the simulation.',
}

strategy: DefaultArgument = {
    'arg': ['--strategy', '-a'],
    'key': 'strategy',
    'default': StrategyType.NO_ATTACKER,
    'help': ('Selection of different attacker strategies. '
             '(Default: %(default)s)'),
}

simulate_scenario: Argument = {
    'arg': ['--simulate-scenario', '-f'],
    'key': 'simulate_scenario',
    'help': 'Path to an OMNeT++ file (omnetpp.ini) of an existing simulation run.',
    'metavar': 'FILE',
}

pseudonym_change: DefaultArgument = {
    'arg': ['--pseudonym-change', '-p'],
    'key': 'pseudonym_change',
    'default': PseudoChangeType.NONE,
    'help': ('Selection of the pseudonym change strategies (PCS) the vehicles should run. '
             '(Default: %(default)s)'),
}

sim_time: DefaultArgument = {
    'arg': ['--sim-time', '-t'],
    'key': 'sim_time',
    'default': 120,
    'help': 'The total simulation time in seconds. (Default: %(default)ss)',
    'metavar': 'SECONDS',
}

seed: DefaultArgument = {
    'arg': ['--seed'],
    'key': 'seed',
    'default': 3,
    'help': 'The seed to initialize the random number generators. (Default: %(default)s)',
}

jobs: DefaultArgument = {
    'arg': ['--jobs', '-j'],
    'key': 'jobs',
    'default': -1,
    'help': ('The maximum number of concurrently running jobs, such as the number of Python worker processes.\n'
             'If -1 all CPUs are used. If 1 is given, no parallel computing code is used at all, which is useful for debugging.\n'
             'For jobs below -1, (n_cpus + 1 + n_jobs) are used. Thus for n_jobs = -2, all CPUs but one are used. '
             '(Default: %(default)s)'),
}

only_generation: Argument = {
    'arg': ['--only-generation'],
    'key': 'only_generation',
    'help': 'Generate everything required for the simulation but do not run it.',
}

dry_run: Argument = {
    'arg': ['--dry-run'],
    'key': 'dry_run',
    'help': ('Preview config which is used to generate and run simulation. '
             'Does not generation configs or runs the simulation.'),
}

# Dynamic Attacker options
attacker_id: DefaultArgument = {
    'arg': ['--attacker-id', '-aid'],
    'key': 'attacker_id',
    'default': None,          # None means that the attacker spawns automatically behind the target
    'help': ('Attacker name shown in the SUMO GUI.\n'
             'Default behavior is that the attacker automatically spawns behind the target.'),
    'metavar': 'ID',
}

target_id: DefaultArgument = {
    'arg': ['--target-id', '-tid'],
    'key': 'target_id',
    'default': None,          # None means that the attacker chooses a random target from the generation list.
    'help': ('Target name shown in the SUMO GUI.\n'
             'Default behavior is that the attacker chooses a target randomly.'),
    'metavar': 'ID',
}

visual_range: DefaultArgument = {
    'arg': ['--visual-range', '-v'],
    'default': 100,
    'key': 'visual_range',
    'help': ('Field of view range in meters the attacker can see to follow his target. '
             '(Default: %(default)sm)'),
    'metavar': 'METERS',
}

spawn_delay: DefaultArgument = {
    'arg': ['--attacker-spawn-delay', '-asd'],
    'key': 'spawn_delay',
    'default': 5,
    'help': ('Spawn delay of the attacker relative to the target in seconds.\n'
             'Spawn delay is ignored when attacker id is set. (Default: %(default)ss)'),
    'metavar': 'SECONDS',
}


# PCS options
pseudonym_lifetime: DefaultArgument = {
    'arg': ['--pseudonym-lifetime'],
    'key': 'pseudonym_lifetime',
    'default': 10,
    'help': ('Time in seconds until next pseudonym change. '
             '(only if \'Periodical\' or \'SLOW\' PCS is active) '
             '(Default: %(default)ss)'),
    'metavar': 'SECONDS',
}

distance_threshold: DefaultArgument = {
    'arg': ['--distance-threshold'],
    'key': 'distance_threshold',
    'default': 500,
    'help': ('Distance driven in meters until next pseudonym change. '
             '(only if \'Distance\' PCS is active) '
             '(Default: %(default)sm)'),
    'metavar': 'METERS',
}

slow_threshold: DefaultArgument = {
    'arg': ['--slow-threshold'],
    'key': 'slow_threshold',
    'default': 30,
    'help': ('The max speed in km/h where a vehicle is considered slow.\n'
             'Slow vehicles do not send CAMs. '
             '(only if \'SLOW\' PCS is active) '
             '(Default: %(default)skm/h)'),
    'metavar': 'SPEED',
}

whisper_road_neighbor_radius: DefaultArgument = {
    'arg': ['--whisper-road-neighbor-radius'],
    'key': 'whisper_road_neighbor_radius',
    'default': 100,
    'help': ('Radius in meters of road neighbors. '
             '(only if \'WHISPER\' PCS is active) '
             '(Default: %(default)sm)'),
    'metavar': 'METERS',
}

whisper_general_neighbor_radius: DefaultArgument = {
    'arg': ['--whisper-general-neighbor-radius'],
    'key': 'whisper_general_neighbor_radius',
    'default': 30,
    'help': ('Radius in meters of general neighbors. '
             '(only if \'WHISPER\' PCS is active) '
             '(Default: %(default)sm)'),
    'metavar': 'METERS',
}

whisper_close_neighbor_radius: DefaultArgument = {
    'arg': ['--whisper-close-neighbor-radius'],
    'key': 'whisper_close_neighbor_radius',
    'default': 30,
    'help': ('Radius in meters of close neighbors. '
             '(only if \'WHISPER\' PCS is active) '
             '(Default: %(default)sm)'),
    'metavar': 'METERS',
}

whisper_counter: DefaultArgument = {
    'arg': ['--whisper-counter'],
    'key': 'whisper_counter',
    'default': 50,
    'help': ('Counter is decremented when CAM messages are send.\n'
             'Pseudonym is changed when a defined threshold is crossed.\n'
             '(only if \'WHISPER\' PCS is active) '
             '(Default: %(default)s)'),
    'metavar': 'COUNTER',
}

cpn_neighbor_radius: DefaultArgument = {
    'arg': ['--cpn-neighbor-radius'],
    'key': 'cpn_neighbor_radius',
    'default': 30,
    'help': ('Radius of neighbors to consider in meters. '
             '(only if \'CPN\' PCS is active) '
             '(Default: %(default)sm)'),
    'metavar': 'METERS',
}

cpn_neighbor_threshold: DefaultArgument = {
    'arg': ['--cpn-neighbor-threshold'],
    'key': 'cpn_neighbor_threshold',
    'default': 3,
    'help': ('Number of neighbors when cooperative pseudonym change is triggered.\n'
             '(only if \'CPN\' PCS is active) '
             '(Default: %(default)s)'),
    'metavar': 'NEIGHBORS',
}

# Hardware
hardware: DefaultArgument = {
    'arg': ['--hardware', '-hw'],
    'key': 'hardware',
    'default': HardwareType.NONE,
    'help': 'Activate hardware integration. (Default: %(default)s)',
}

hardware_veh_id: DefaultArgument = {
    'arg': ['--hardware-veh-id', '-hid'],
    'key': 'hardware_veh_id',
    'default': None,
    'help': 'Vehicle name shown in the SUMO GUI which has the hardware connection.',
    'metavar': 'ID',
}

hardware_local_ip: DefaultArgument = {
    'arg': ['--hardware-local-ip'],
    'key': 'hardware_local_ip',
    'default': '192.168.11.10',
    'help': 'Local IP address of the hardware. (Default: %(default)s)',
    'metavar': 'IP',
}

hardware_local_port: DefaultArgument = {
    'arg': ['--hardware-local-port'],
    'key': 'hardware_local_port',
    'default': 4400,
    'help': 'Local Port of the hardware. (Default: %(default)s)',
    'metavar': 'PORT',
}

hardware_remote_ip: DefaultArgument = {
    'arg': ['--hardware-remote-ip'],
    'key': 'hardware_remote_ip',
    'default': '192.168.11.11',
    'help': 'Remote IP address of the hardware. (Default: %(default)s)',
    'metavar': 'IP',
}

hardware_remote_port: DefaultArgument = {
    'arg': ['--hardware-remote-port'],
    'key': 'hardware_remote_port',
    'default': 4401,
    'help': 'Remote Port of the hardware. (Default: %(default)s)',
    'metavar': 'PORT',
}
