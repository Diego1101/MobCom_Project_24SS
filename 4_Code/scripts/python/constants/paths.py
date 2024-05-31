# Python file contains all path constants

# @author  Annette Grueber (WS21/22)
# @author  Andre Vaskevic (WS21/22)
# @author  Marek Parucha (WS21/22)
# @author  Martin Dell (WS22/23)
# @author  Janis Latus (WS22/23)
# @author  Kadir Özer (WS22/23)
# @date    29.12.2022

import os
from os.path import join, realpath
from pathlib import Path

from exceptions.sumo import UnconfiguredEnvironmentError

from enums.FileType import FileType
from enums.FolderType import FolderType

from enums.HardwareType import HardwareType
from enums.LogFileType import LogFileType
from enums.PseudoChangeType import PseudoChangeType
from enums.StrategyType import StrategyType


# For all scenarios
sumo_home = 'SUMO_HOME'
if sumo_home not in os.environ:
    raise UnconfiguredEnvironmentError(f'Environment variable "{sumo_home}" is not declared.')

sumo_tools_path = join(os.environ[sumo_home], 'tools')
root_dir = Path(realpath(__file__)).parent.parent.parent.parent.absolute()  # Resolves to 4_Code folder

# Folder paths
scenarios_dir = join(root_dir, 'scenarios')
resources_dir = join(root_dir, 'resources')
templates_dir = join(resources_dir, 'templates')
services_dir = join(resources_dir, 'services')
build_dir = join(root_dir, 'build')
scenario_build_dir = join(build_dir, 'scenarios')

log_filenames = {
    LogFileType.SUMO: 'sumo_log.xml',
    LogFileType.TRACI: 'traci.log',
    LogFileType.DUAROUTER: 'duarouter.log'
}

dirnames = {
    FolderType.LOGS: 'logs',
    FolderType.TEMP: '_temp'
}

# Scenario resources in simulation run
scenario_filenames = {
    FileType.ROUTE: 'traffic.trips.xml',
    FileType.VALIDATED_ROUTE: 'validated_traffic.trips.xml',

    FileType.GLOBAL_CONFIG: 'config_dump.yml',
    FileType.ATTACKER_INFO: 'attacker_info.yml',
}

# Scenario resources outside simulation run
resource_filenames = {
    FileType.ADD: 'add.xml',
    FileType.NET: 'net.xml',
    FileType.VIEW: 'view.xml',

    FileType.DEN_USE_CASE: 'den_use_cases.xml',
}

# Files
static_paths = {
    # cmake
    FileType.CMAKE_PARENT_TEMPLATE: join(templates_dir, 'CMakeLists.txt'),
    FileType.CMAKE_CHILD_TEMPLATE: join(templates_dir, 'CMakeLists.child.template.txt'),

    # OMNET++
    FileType.OMNET_INI_TEMPLATE: join(templates_dir, 'omnetpp.template.ini'),

    # SUMO
    FileType.SUMO_CONFIG_TEMPLATE: join(templates_dir, 'sumocfg.template.xml'),

    # Artery
    FileType.ARTERY_SENSORS: join(templates_dir, 'sensors.xml'),

    # Directories
    FileType.NED: services_dir,
    FileType.RESULTS: scenarios_dir,
}

# Run files
build_script_file = join(root_dir, 'scripts', 'bash', 'build_project.sh')
artery_script_file = join(build_dir, 'artery', 'run_artery.sh')

# Base services which need to be included in every simulation
base_services_xml_templates = [
    join(templates_dir, 'service.logger.template.xml'),
]

strategy_xml_templates = {
    StrategyType.NO_ATTACKER: join(templates_dir, 'service.no_attacker.template.xml'),
    StrategyType.ATTACKER_SERVICE: join(templates_dir, 'service.with_attacker.template.xml'),
}

hardware_xml_templates = {
    HardwareType.COHDA: join(templates_dir, 'service.with_hw.template.xml'),
}

omnet_config_templates = {
    PseudoChangeType.PERIODICAL: join(templates_dir, 'periodicalPCConfig.template.ini'),
    PseudoChangeType.SLOW: join(templates_dir, 'slowPCConfig.template.ini'),
    PseudoChangeType.DISTANCE: join(templates_dir, 'distancePCConfig.template.ini'),
    PseudoChangeType.WHISPER: join(templates_dir, 'whisperPCConfig.template.ini'),
    PseudoChangeType.CPN: join(templates_dir, 'cooperativePCConfig.template.ini'),

    HardwareType.COHDA: join(templates_dir, 'hwConfig.template.ini'),

    StrategyType.ATTACKER_SERVICE: join(templates_dir, 'attackerServiceConfig.template.ini'),
}

file_extensions = {
    FileType.SUMO_CONFIG_TEMPLATE: '.sumocfg',
    FileType.OMNET_INI_TEMPLATE: '.ini',
    FileType.LIBRARY: '.so',
    FileType.SERVICE_TEMPLATE: '.xml',
    FileType.CMAKE_CHILD_TEMPLATE: '.txt',
    FileType.CMAKE_PARENT_TEMPLATE: '.txt',
}

prefix = {
    FileType.OMNET_INI_TEMPLATE: 'omnetpp',
    FileType.SERVICE_TEMPLATE: 'services',

    FileType.CMAKE_CHILD_TEMPLATE: 'CMakeLists',
    FileType.CMAKE_PARENT_TEMPLATE: 'CMakeLists',
}

# Metrics
esslingen_map_filename = 'map_esslingen.png'
esslingen_imap_filename = 'map_esslingen.html'
esslingen_map = join(resources_dir, esslingen_map_filename)


metrics_dirname = 'metrics'
dynamic_attacker_dirname = 'dynamic_attacker'
static_attacker_dirname = 'static_attacker'
anonymity_dirname = 'anonymity'
consumption_dirname = 'consumption'

cam_csv = 'cams.csv'
cam_temp_csv = 'cams.csv.tmp'
dynamic_attacker_csv = 'dynamic_attacker.csv'
vehicles_csv = 'vehicles.csv'

pseudonym_consumption = 'pseudonym_consumption.csv'
pseudonym_consumption_stats = 'pseudonym_consumption_stats.txt'
pseudonym_consumption_plot = 'pseudonym_consumption_characteristics.png'

tracking_success = 'tracking_success.txt'
