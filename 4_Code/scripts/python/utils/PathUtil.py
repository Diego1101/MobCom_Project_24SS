# Python file with all utils for the files and folders of the project

# @author  Annette Grueber (WS21/22)
# @author  Martin Dell (WS22/23)
# @date    15.11.2022

import os
import shutil
from typing import Union
import constants.paths as cpaths
from enums.FileType import FileType
from enums.FolderType import FolderType
from enums.HardwareType import HardwareType
from enums.LogFileType import LogFileType
from enums.PseudoChangeType import PseudoChangeType
from enums.ScenarioType import ScenarioType
from enums.StrategyType import StrategyType
from utils.configuration import SimConfig


def get_scenario_dir(scenario: ScenarioType) -> str:
    """Return the directory for given scenario.
    """
    return os.path.join(cpaths.scenarios_dir, str(scenario))


def get_resource_dir(scenario: ScenarioType) -> str:
    """Return the resource directory for given scenario.
    """
    return os.path.join(cpaths.resources_dir, str(scenario))


def get_simulation_name(cfg: SimConfig) -> str:
    """Get the name of the current simulation configuration.
    This name is also the result directory name.

    Args:
        cfg (SimConfig): Simulation configuration.

    Returns:
        str: Simulation name.
    """
    return f'strat={cfg.attacker.strategy}+pcs={cfg.pcs.strategy}+traffic={cfg.spawn_rate}+t={cfg.sim_time}'


def get_prefix(scenario: ScenarioType, file_type: FileType) -> str:
    """Return the prefix for given file type.
    """
    return cpaths.prefix.get(file_type, f'{scenario.value}_config')


def get_simulation_dir(cfg: SimConfig) -> str:
    """Returns the path of the directory where all the relevant files (omnetpp.ini, service.xml..) are written to.

    Args:
        cfg (SimConfig): Simulation configuration.

    Returns:
        str: The directory of the simulation run.
    """
    scenario_dir = get_scenario_dir(cfg.scenario)
    sim_name = get_simulation_name(cfg)

    return os.path.join(scenario_dir, sim_name)


def makedir(folder_type: FolderType, cfg: SimConfig) -> str:
    """Creates directory based on folder type. Does nothing if directory already exists.

    Args:
        folder_type (FolderType): The type of directory to create.
        cfg (SimConfig): Simulation configuration.

    Raises:
        ValueError: Unknown or unsupported folder type.

    Returns:
        str: The path of the created directory.
    """
    sim_dir = get_simulation_dir(cfg)

    dir_path = ''
    if folder_type == FolderType.SCENARIO:
        dir_path = sim_dir
    elif folder_type in cpaths.dirnames:
        dir_path = os.path.join(sim_dir, cpaths.dirnames[folder_type])

    if not dir_path:
        raise ValueError(f'Unknown or unsupported folder type {folder_type}.')

    os.makedirs(dir_path, exist_ok=True)

    return dir_path


def copy(file: str, cfg: SimConfig):
    """Copies the `file` to the simulation folder.

    Args:
        file (str): File path to copy.
        cfg (SimConfig): Simulation configuration.
    """
    sim_dir = get_simulation_dir(cfg)
    file_name = os.path.basename(file)

    shutil.copy(file, os.path.join(sim_dir, file_name))


def get_path(type: Union[FileType, FolderType], cfg: SimConfig, *, must_exist=False) -> str:
    """Returns the mapped path to a file or directory to the given type.

    Args:
        type (FileType|FolderType): File or folder to get.
        cfg (SimConfig): Simulation configuration.
        must_exist (bool, optional): If true the function checks if the returned path exists on disk.
                                     If it does not exist an error is raised. Defaults to False.

    Raises:
        ValueError: There is no path to the given file type.
        FileNotFoundError: There is a path to the given file type but it does not exist on disk.

    Returns:
        str: Mapped path to a file to the file type.
    """

    path = ''

    if type in cpaths.static_paths:
        path = cpaths.static_paths[type]

    elif type in cpaths.resource_filenames:
        sim_resource_path = get_resource_dir(cfg.scenario)
        path = os.path.join(sim_resource_path, cpaths.resource_filenames[type])

    elif type in cpaths.scenario_filenames:
        sim_dir = get_simulation_dir(cfg)
        path = os.path.join(sim_dir, cpaths.scenario_filenames[type])

    elif (type == FileType.SERVICE_TEMPLATE
          and cfg.attacker.strategy in cpaths.strategy_xml_templates):
        path = cpaths.strategy_xml_templates[cfg.attacker.strategy]

    elif type == FileType.LIBRARY:
        lib_filename = f'libartery_{cfg.scenario}{cpaths.file_extensions[FileType.LIBRARY]}'
        path = os.path.join(cpaths.scenario_build_dir, str(cfg.scenario), lib_filename)

    elif type == FolderType.SCENARIO:
        path = get_simulation_dir(cfg)

    elif type in cpaths.dirnames:
        sim_dir = get_simulation_dir(cfg)
        path = os.path.join(sim_dir, cpaths.dirnames[type])

    if not path:
        raise ValueError(f'File type {type} does not map to any path.')

    # Check if file path really exist
    if (must_exist and not os.path.exists(path)):
        raise FileNotFoundError(f'Found path {path} for file type {type} but it does not exist on disk.')

    return path


def get_log(type: LogFileType, cfg: SimConfig) -> str:
    """
    Returns the path to the type of log file.
    If log folder does not exist, it will be created.

    Args:
        type (LogFileType): Type of log file to get.
        cfg (SimConfig): Simulation configuration.

    Raises:
        ValueError: Log file type not supported.

    Returns:
        str: Path to requested log file.
    """
    if type not in cpaths.log_filenames:
        raise ValueError(f'Log file type {type} does not map to any path.')

    log_dir = makedir(FolderType.LOGS, cfg)
    file_name = cpaths.log_filenames[type]
    return os.path.join(log_dir, file_name)


def get_sumo_config_file(cfg: SimConfig) -> str:
    """
    Return the path to the SUMO config file and
    creates simulation folder if it does not exist.

    Args:
        cfg (SimConfig): Simulation configuration.

    Returns:
        str: Path to SUMO config file.
    """
    prefix = get_prefix(cfg.scenario, FileType.SUMO_CONFIG_TEMPLATE)
    ext = cpaths.file_extensions.get(FileType.SUMO_CONFIG_TEMPLATE, '')
    sim_dir = makedir(FolderType.SCENARIO, cfg)

    return os.path.join(sim_dir, prefix + ext)


def get_omnet_config_template(file_type: Union[PseudoChangeType, HardwareType, StrategyType]) -> str:
    """Returns full path of the OMNet++ template ini file.
    """
    return cpaths.omnet_config_templates.get(file_type, '')


def get_xml_template_paths(strategy: StrategyType, hardware: HardwareType):
    """Returns the needed service template paths by given parameters(strategy and hardware)
    """
    paths = []

    paths += cpaths.base_services_xml_templates

    if strategy in cpaths.strategy_xml_templates:
        paths.append(cpaths.strategy_xml_templates[strategy])

    if hardware in cpaths.hardware_xml_templates:
        paths.append(cpaths.hardware_xml_templates[hardware])

    return paths
