#!/usr/bin/env python3

# Starting point of simulation.

# @author  Marek Parucha (WS21/22)
# @author  Martin Dell (WS22/23)
# @date    18.11.2022

import os
import random
import subprocess
import sys
from typing import Optional
import numpy as np

import constants.paths as cpaths
from enums.HardwareType import HardwareType
from enums.StrategyType import StrategyType
from exceptions.hardware import NoHardwareVehicleIdError
import sumo_runner
import utils.FileMergerUtil as FileMergerUtil
import utils.PathUtil as PathUtil
import utils.TemplateUtil as TemplateUtil
from enums.FileType import FileType
from Gui import Gui
from utils.configuration import SimConfig
from argparsers.RunnerArgumentParser import RunnerArgumentParser


def run_generation(cfg: SimConfig, gui: Optional[Gui] = None):
    """Creates all necessary configuration files for the simulation and starts it.

    Args:
        cfg (SimConfig): Simulation configuration.
        gui (Optional[Gui], optional): GUI object if it was called from GUI.
                                       Needed to cleanly close GUI or display errors. Defaults to None.
    """

    print('Current configuration:')  # TODO: Move to logger
    print(cfg)

    # Dump complete config to scenario folder
    cfg_dump_file = PathUtil.get_path(FileType.GLOBAL_CONFIG, cfg, must_exist=False)
    os.makedirs(os.path.dirname(cfg_dump_file), exist_ok=True)
    cfg.dump(cfg_dump_file)

    if cfg.is_dry_run:
        return

    print('Generating configuration files and routes ...')  # TODO: Move to logger

    if cfg.hardware.type != HardwareType.NONE and cfg.hardware.hardware_veh_id is None:
        raise NoHardwareVehicleIdError('Hardware integration is enabled but vehicle id is missing.')

    # Generate SUMO configs and routes
    sumo_runner.generate_configs(cfg)

    ini_file = create_ini_config(cfg)
    create_service_files(cfg)

    # Dump SUMO IDs of attacker and target into separate file.
    if cfg.attacker.strategy == StrategyType.ATTACKER_SERVICE:
        attacker_info_file = PathUtil.get_path(FileType.ATTACKER_INFO, cfg, must_exist=False)
        cfg.attacker.dump_attacker_info(attacker_info_file)

    print('Done generating configuration files and routes.')

    if cfg.run_only_generation:
        return

    ini_file_path = os.path.join(PathUtil.get_simulation_dir(cfg), ini_file)

    # Start simulation
    start_simulation(cfg.no_sumo_gui, ini_file_path, gui)


def start_simulation(no_sumo_gui: bool, ini_file_path: str, gui: Optional[Gui] = None):
    """
    Starts the simulation with artery.
    Builds the required services first if needed.

    Args:
        no_sumo_gui (bool): If simulation should run in console (True) or in SUMO GUI (False).
        ini_file_path (str): Path to the OMNet++ configuration file.
        gui (Optional[Gui], optional): GUI object if it was called from GUI.
                                       Needed to cleanly close GUI or display errors. Defaults to None. Defaults to None.
    """

    print('\nBuilding simulation ...')  # TODO: Move to logger
    success = run_command([f'{cpaths.build_script_file}'], 'CMake error:\n\nSee console output for more information.', gui)
    if not success:
        return

    sim_dir = os.path.dirname(os.path.abspath(ini_file_path))

    print('\nCurrent simulation run name:')  # TODO: Move to logger
    print(os.path.basename(sim_dir))

    omnet_filename = os.path.basename(ini_file_path)

    # Go to the selected simulation folder and make the artery script runnable
    commands = [
        f'cd {sim_dir}',
        f'chmod +x {cpaths.artery_script_file}'
        ]

    print('\nStarting simulation ...')  # TODO: Move to logger
    # Start the run with a GUI if requested.
    if not no_sumo_gui:
        commands.append(f'{cpaths.artery_script_file} -f {omnet_filename}')
    else:
        commands.append(f'{cpaths.artery_script_file} -u Cmdenv --cmdenv-status-frequency=5s -f {omnet_filename} ')

    success = run_command(commands, 'Artery script error', gui)
    if not success:
        return

    print('\nSimulation done. Check scenario folder to see results:')
    print(sim_dir)

    if gui is not None:
        gui.running = False
        gui.generating_finished = True


def run_command(commands: 'list[str]', error_message: str, gui: Optional[Gui] = None):
    """
    Method runs given commands and sets the error flag
    if a process returns an error code.
    """
    # Executes a single run with the created temporary files.
    result = subprocess.run(';'.join(commands), shell=True)

    if result.returncode != 0:
        if gui is not None:
            gui.error_message = error_message
            gui.error = True

        return False

    return True


def create_ini_config(cfg: SimConfig) -> str:
    """Calls method that creates the OMNet++ file and returns the file
    """
    try:
        sim_dir = PathUtil.get_simulation_dir(cfg)
        return TemplateUtil.create_file_from_template(sim_dir, FileType.OMNET_INI_TEMPLATE, cfg)
    except Exception as e:
        raise Exception('Could not create OMNet++ ini file.') from e


def create_service_files(cfg: SimConfig):
    """Creates all artery middleware service configuration files.

    Args:
        cfg (SimConfig): Simulation configuration.

    Raises:
        Exception: Creation of service files failed.
    """
    try:
        # Get relevant xml template paths
        xml_paths = PathUtil.get_xml_template_paths(cfg.attacker.strategy, cfg.hardware.type)

        # Create service file from template
        sim_dir = PathUtil.get_simulation_dir(cfg)
        ext = cpaths.file_extensions[FileType.SERVICE_TEMPLATE]
        prefix = PathUtil.get_prefix(cfg.scenario, FileType.SERVICE_TEMPLATE)
        FileMergerUtil.merge_xml_templates(xml_paths, os.path.join(sim_dir, prefix + ext), cfg)

        # Copy additional files
        for additional_file in TemplateUtil.get_additional_files(cfg):
            PathUtil.copy(additional_file, cfg)

        # Create local Cmake file from template
        scenario_dir = PathUtil.get_scenario_dir(cfg.scenario)
        TemplateUtil.create_file_from_template(scenario_dir, FileType.CMAKE_CHILD_TEMPLATE, cfg)

    except Exception as e:
        raise Exception('Creation of service files failed.') from e


def set_seeds(seed: int):
    """Initialize the random number generators.

    Args:
        seed (int): Seed with which to initialize the random number generators.
    """
    random.seed(seed)
    np.random.seed(seed)


def main():
    """Main entry point when executing this file.
    """

    # Parse the arguments which defined in the argument parser
    parser = RunnerArgumentParser()
    args = parser.parse_args()

    # Parse configuration
    cfg = SimConfig(vars(args))

    set_seeds(cfg.seed)

    # If no arguments are given open gui, otherwise start simulation in console.
    if len(sys.argv) == 1:
        gui = Gui(run_generation, start_simulation)
        gui.run_gui()
    elif cfg.simulate_scenario is not None and not cfg.run_only_generation:
        # If path to omnet file is given just start the simulation without generating new files (except logs of course)
        start_simulation(cfg.no_sumo_gui, cfg.simulate_scenario)
    else:
        run_generation(cfg)


if __name__ == '__main__':
    main()
