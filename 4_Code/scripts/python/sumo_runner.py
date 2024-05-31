# Python file to create a sumo simulation

# @author  Annette Grueber (WS21/22)
# @author  Martin Dell (WS22/23)
# @date    15.11.2022

import os
import sys
from typing import Optional

import constants.paths as cpaths
from enums.LogFileType import LogFileType
import utils.PathUtil as PathUtil
import utils.TemplateUtil as TemplateUtil
from argparsers.RunnerArgumentParser import RunnerArgumentParser
from enums.FileType import FileType
from enums.FolderType import FolderType
from exceptions.sumo import UnconfiguredEnvironmentError
from generators.route_generator import generate_routes
from utils.configuration import SimConfig

# To import the sumolib:
# Add the the <SUMO_HOME>/tools path to the python load path if the environment variable SUMO_HOME exist.
if cpaths.sumo_home not in os.environ:
    raise UnconfiguredEnvironmentError(f'Environment variable "{cpaths.sumo_home}" is not declared.')
else:
    sys.path.append(cpaths.sumo_tools_path)

    import traci
    from sumolib import checkBinary


def generate_configs(cfg: SimConfig) -> str:
    """Generated SUMO config (`.sumocfg`) and trips/routes for vehicles.

    Args:
        cfg (SimConfig): Simulation configuration.

    Returns:
        str: Path to the SUMO configuration file.
    """
    # Create directory for sumo scenario files
    PathUtil.makedir(FolderType.SCENARIO, cfg)

    # Create the route files
    generate_routes(cfg)

    # Create the sumo config file
    return create_config_file(cfg)


def create_config_file(cfg: SimConfig) -> str:
    """Create the SUMO configuration file (`.sumocfg`).

    Args:
        cfg (SimConfig): Simulation configuration.

    Raises:
        Exception: Creation of SUMO config file failed.

    Returns:
        str: Path to the created file.
    """
    try:
        # Create directory for sumo scenario files
        sim_dir = PathUtil.makedir(FolderType.SCENARIO, cfg)

        # Create sumocfg file from template
        sumocfg = TemplateUtil.create_file_from_template(sim_dir, FileType.SUMO_CONFIG_TEMPLATE, cfg)

        return os.path.join(sim_dir, sumocfg)
    except Exception as e:
        raise Exception('Creation of SUMO config file failed.') from e


def start_sumo_gui_server(sumo_cfg_path: str, traci_log: Optional[str] = None):
    """Starts the SUMO GUI.

    Args:
        sumo_cfg_path (str): Path to the SUMO config file.
        traci_log (Optional[str], optional): Path to a log file where traci can write to. Defaults to None.
    """
    # This script has been called from the command line. It will start sumo-gui as a server, then connect and run
    sumo_bin = checkBinary('sumo-gui')

    # Sumo is started as a subprocess and then the python script connects and runs
    traci.start([sumo_bin, '-c', sumo_cfg_path], traceFile=traci_log)

    while traci.simulation.getMinExpectedNumber() > 0:  # type: ignore
        traci.simulationStep()

    traci.close()
    sys.stdout.flush()


def main():
    """
    Main entry point if this script is called from console.
    This is mainly here for debugging purposes.

    Raises:
        Exception: Could not start sumo-gui.
    """
    # Parse the arguments which defined in the argument parser
    parser = RunnerArgumentParser()
    args = parser.parse_args()
    cfg = SimConfig(vars(args))

    sumo_cfg_path = generate_configs(cfg)

    if cfg.no_sumo_gui or cfg.run_only_generation:
        return


    traci_log = PathUtil.get_log(LogFileType.TRACI, cfg) if not cfg.no_logging else None
    try:
        # Start sumo-gui as a server
        start_sumo_gui_server(sumo_cfg_path, traci_log)
    except Exception as e:
        raise Exception('Could not start sumo-gui.') from e


if __name__ == '__main__':
    main()
