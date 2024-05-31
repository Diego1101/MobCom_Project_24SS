# Python file with all utils for template files

# @author  Annette Grueber (WS21/22)
# @author  Martin Dell (WS22/23)
# @date    18.11.2022

import os
from typing import Any, Optional

import constants.template_vars as tempkeys
import constants.paths as cpaths
from enums.LogFileType import LogFileType
from enums.StrategyType import StrategyType
import utils.PathUtil as PathUtil
from enums.FileType import FileType
from utils.configuration import SimConfig


def create_file_from_template(sim_dir: str, file_type: FileType, cfg: SimConfig, ext: str = '') -> str:
    """
    Creates the given file type from a template and fills in
    all required data using the simulation configuration.

    Args:
        sim_dir (str): Path to the simulation directory.
        file_type (FileType): File type to create.
        cfg (SimConfig): Simulation configuration.
        ext (str, optional): Extension to add to the created file.
                             By default it will try to infer the extension automatically.

    Raises:
        Exception: Could not create file from template.

    Returns:
        str: Path to the created file.
    """
    try:
        prefix = PathUtil.get_prefix(cfg.scenario, file_type)

        extension = ext
        if not extension:
            extension = cpaths.file_extensions.get(file_type, '')

        sim_cfg_file = os.path.join(sim_dir, prefix + extension)

        template_file = PathUtil.get_path(file_type, cfg, must_exist=True)

        replacements = get_replacements(file_type, cfg)

        return new_file(template_file, cfg, replacements, sim_cfg_file)

    except Exception as e:
        raise Exception(f'Could not create file {file_type} from template.') from e


def new_file(template_path: str, cfg: SimConfig, replacements: dict, path: str) -> str:
    """Creates a new file from a template and fills in the placeholders.

    Args:
        template_path (str): Path to the template file to copy.
        cfg (SimConfig): Simulation configuration used to fill in the placeholders.
        replacements (dict): Additional data used to fill in the placeholders. DictKeys represent the placeholder keys.
        path (str): Path where to create the new file.

    Raises:
        Exception: Could not replace placeholders in template.

    Returns:
        str: Path of the created file.
    """
    content = replace_in_templates(template_path, cfg, replacements)

    if not content:
        raise Exception(f'Could not replace variables in template {template_path}')

    with open(path, 'w') as f:
        f.write(content)

    return path


def get_replacements(file_type: FileType, cfg: SimConfig) -> 'dict[str, Any]':
    """
    Get the required replacement data used to fill in
    template placeholder variables of given file type.

    Args:
        file_type (FileType): File type for which to get replacement data.
        cfg (SimConfig): Simulation configuration.

    Returns:
        dict[str, Any]: Replacements used to fill in template placeholder variables.
                        DictKeys correspond to placeholder keys.
    """
    if file_type == FileType.SUMO_CONFIG_TEMPLATE:
        network_file = PathUtil.get_path(FileType.NET, cfg)
        route_file = PathUtil.get_path(FileType.ROUTE, cfg)
        additional_file = PathUtil.get_path(FileType.ADD, cfg)
        view_setting_file = PathUtil.get_path(FileType.VIEW, cfg)

        replacement = {
            tempkeys.network_file_key: network_file,
            tempkeys.route_file_key: route_file,
            tempkeys.additional_file_key: additional_file,
            tempkeys.view_file_key: view_setting_file
            }

        output_block = ''
        if not cfg.no_logging:
            log_file = PathUtil.get_log(LogFileType.SUMO, cfg)
            output_block = f'<output>\n<tripinfo-output value=\"{log_file}\"/>\n<output-prefix value=\"TIME_\"/>\n</output>'

        replacement[tempkeys.output_block_key] = output_block

        return replacement

    elif file_type == FileType.CMAKE_CHILD_TEMPLATE:
        ned_base_file = PathUtil.get_path(FileType.NED, cfg)
        replacement = {
            tempkeys.sim_key: PathUtil.get_simulation_name(cfg),
            tempkeys.ned_base_dir_key: ned_base_file
            }

        return replacement

    elif file_type == FileType.OMNET_INI_TEMPLATE:
        return get_omnet_replacements(cfg)

    return {}


def replace_in_templates(template_path: str, cfg: SimConfig, replacements: 'Optional[dict[str, Any]]' = None) -> str:
    """
    Copies the content of the template file and
    replaces the placeholders with given replacements and simulation configuration.

    Args:
        template_path (str): Path to template file to copy.
        cfg (SimConfig): Simulation configuration used to fill in the placeholders.
                         All placeholders starting with `$cfg.*$` will be replaced with the corresponding config value.
        replacements (Optional[dict[str, Any]], optional): Additional data used to fill in the placeholders. Defaults to None.

    Raises:
        Exception: Unknown config placeholders ($cfg.*$) found in template file.

    Returns:
        str: Content of template file but all placeholders have been filled in with data.
    """
    with open(template_path, 'r') as template:
        contents = template.read()

    # Replace config variables
    for key, value in cfg.items():
        if isinstance(value, bool):
            replace_value = str(value).lower()
        else:
            replace_value = str(value)

        contents = contents.replace(f'$cfg.{key}$', replace_value)

    if contents.find('$cfg.') != -1:
        raise Exception(f'Unknown config placeholders ($cfg.*$) found in template file {template_path}.')

    if replacements is None:
        return contents

    # Replace custom variables
    for key, value in replacements.items():
        if isinstance(value, bool):
            replace_value = str(value).lower()
        else:
            replace_value = str(value)

        contents = contents.replace(f'${key}$', replace_value)

    return contents


def get_omnet_replacements(cfg: SimConfig) -> 'dict[str, Any]':
    """Returns the necessary OMNet++ configuration placeholder replacements.

    Args:
        cfg (SimConfig): Simulation configuration.

    Returns:
        dict[str, Any]: Replacements used to fill in OMNet++ template placeholder variables.
                        DictKeys correspond to placeholder keys.
    """
    attacker_cfg = PathUtil.get_omnet_config_template(cfg.attacker.strategy)
    hardware_cfg = PathUtil.get_omnet_config_template(cfg.hardware.type)
    pseudo_cfg = PathUtil.get_omnet_config_template(cfg.pcs.strategy)

    # There are configurations where there is no OMNet++ config template available.
    # In this case get_omnet_config_template returns an empty string
    # Check if a path was returned before calling replace_in_templates

    attacker_replacements = {
        tempkeys.dynamic_attacker_logfile_key: cpaths.dynamic_attacker_csv,
    }

    replacement = {
        tempkeys.lib_file_key: PathUtil.get_path(FileType.LIBRARY, cfg),
        tempkeys.ned_base_dir_key: PathUtil.get_path(FileType.NED, cfg),
        tempkeys.results_dir_key: PathUtil.get_path(FileType.RESULTS, cfg),
        tempkeys.sumo_launcher_key: 'sumo' if cfg.no_sumo_gui else 'sumo-gui',
        tempkeys.sumo_config_file_key: PathUtil.get_sumo_config_file(cfg),
        tempkeys.attacker_service_key: replace_in_templates(attacker_cfg, cfg, replacements=attacker_replacements) if attacker_cfg else '',
        tempkeys.with_hw_key: replace_in_templates(hardware_cfg, cfg) if hardware_cfg else '',
        tempkeys.pseudo_service_key: replace_in_templates(pseudo_cfg, cfg) if pseudo_cfg else '',

        tempkeys.cam_logfile_key: cpaths.cam_csv,
        tempkeys.vehicles_logfile_key: cpaths.vehicles_csv,
    }

    return replacement


def get_additional_files(cfg: SimConfig) -> 'list[str]':
    """
    Returns all additional files which need to be copied
    to the simulation directory unchanged.

    Args:
        cfg (SimConfig): Simulation configuration.

    Returns:
        list[str]: List of files which need to be copied.
    """
    files = []

    if cfg.attacker.strategy == StrategyType.ATTACKER_SERVICE:
        files.append(PathUtil.get_path(FileType.ARTERY_SENSORS, cfg, must_exist=True))

    return files
