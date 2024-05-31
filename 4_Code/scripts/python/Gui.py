# Gui that lets the user select the values for simulation. Returns selected values.

# @author  Marek Parucha (WS21/22)
# @author  Martin Dell (WS22/23)
# @author  Kevin Ehling (WS22/23)
# @author  Janis Latus (WS22/23)
# @date    20.12.2022

import threading
from typing import Any, Callable

import constants.arguments as args
import constants.paths as cpaths
import PySimpleGUI as sg
from enums.HardwareType import HardwareType
from enums.PseudoChangeType import PseudoChangeType
from enums.ScenarioType import ScenarioType
from enums.StrategyType import StrategyType
from utils.configuration import SimConfig


class Gui:
    """GUI to configure and start simulation.
    """
    def __init__(self, generation_method: Callable, simulation_method: Callable):
        self.generation_method = generation_method
        self.simulation_method = simulation_method

        self.running = False
        self.generating_finished = False
        self.error = False
        self.error_message = ''

    def create_layout(self):
        """Creates layout for the window with relevant gui elements and the associated values.
        """
        sg.theme('DarkAmber')  # Add a touch of color
        # Simple Layout with all relevant values
        return [[sg.Text('Pseudonym testing for V2X Communication')],
                [sg.Radio('Generate and start scenario', 'generateScenarioRadio', key='generateScenarioRadioTrue',
                          default=True, enable_events=True),
                 sg.Radio('Only start selected scenario', 'generateScenarioRadio', key='generateScenarioRadioFalse',
                          enable_events=True, default=False)],
                [sg.Frame('Without generating', [[sg.Text('Select Omnet++ file:', size=(30, 1), key='scenarioPathText'),
                                                  sg.In(key='scenarioPathIn', disabled=True, tooltip=self._tooltip(args.simulate_scenario)),
                                                  sg.FileBrowse(file_types=(('Omnet file', '*.ini'),),
                                                                initial_folder=cpaths.scenarios_dir, key='scenarioPathBrowse',
                                                                disabled=True)]])],

                [sg.Frame('With generating', [
                    [sg.Text('Selection of the scenario to be simulated:', key='scenarioOptionsText', size=(60, 1)),
                     sg.Combo(values=list(ScenarioType), key='scenarioOptionsCombo', default_value=args.scenario['default'],
                              tooltip=self._tooltip(args.scenario), readonly=True)],

                    [sg.Text('Maximum simulation time [sec]:', size=(60, 1)),
                     sg.In(size=(10, 1), key='simTimeIn', default_text=args.sim_time['default'],
                           tooltip=self._tooltip(args.sim_time))],

                    [sg.Text('Approximate spawn rate of vehicles per minute in the simulation:', size=(60, 1)),
                     sg.In(size=(10, 1), key='spawnRateIn', default_text=args.spawn_rate['default'],
                           tooltip=self._tooltip(args.spawn_rate))],

                    [sg.Text('Start simulation with GUI:', size=(60, 1)),
                     sg.Checkbox(text='', key='sumoGuiOptionsCheckbox', default=False)],

                    [sg.Text('Enable logging:', size=(60, 1)),
                     sg.Checkbox(text='', key='loggingOptionsCheckbox', default=False)],

                    [sg.Text('Seed:', size=(60, 1)),
                     sg.In(size=(10, 1), key='seedIn', default_text=args.seed['default'], tooltip=self._tooltip(args.seed))],

                    [sg.Text('Workers:', size=(60, 1)),
                     sg.In(size=(10, 1), key='jobsIn', default_text=args.jobs['default'], tooltip=self._tooltip(args.jobs))],

                    [sg.Text('Selection of different attacker strategies:', size=(60, 1)),
                     sg.Combo(values=list(StrategyType), key='strategyOptionsCombo', default_value=args.strategy['default'],
                              tooltip=self._tooltip(args.strategy), readonly=True, enable_events=True)],
                    [sg.pin(sg.Column([[sg.Text('Attacker ID:', size=(35, 1)),
                                        sg.In(size=(20, 1), key='attackerIdIn', default_text=args.attacker_id['default'],
                                              tooltip=self._tooltip(args.attacker_id))],
                                       [sg.Text('Target ID:', size=(35, 1)),
                                        sg.In(size=(20, 1), key='targetIdIn', default_text=args.target_id['default'],
                                              tooltip=self._tooltip(args.target_id))],
                                       [sg.Text('Spawn delay [sec]:', size=(35, 1)),
                                        sg.In(size=(20, 1), key='spawnDelayIn', default_text=args.spawn_delay['default'],
                                              tooltip=self._tooltip(args.spawn_delay))],
                                       [sg.Text('Visual range [m]:', size=(35, 1)),
                                        sg.In(size=(20, 1), key='visualRangeIn', default_text=args.visual_range['default'],
                                              tooltip=self._tooltip(args.visual_range))]],
                                      visible=False, key='attackerParam'))],

                    [sg.Text('Selection of different Pseudonym change strategies:', size=(60, 1)),
                     sg.Combo(values=list(PseudoChangeType), key='pseudoOptionsCombo', default_value=args.pseudonym_change['default'],
                              tooltip=self._tooltip(args.pseudonym_change), readonly=True, enable_events=True)],
                    [sg.pin(sg.Column([[sg.Text('Time until next pseudonym change [sec]:', size=(35, 1)),
                                        sg.In(size=(10, 1), key='pseudoLifetimeIn', default_text=args.pseudonym_lifetime['default'],
                                              tooltip=self._tooltip(args.pseudonym_lifetime))]],
                                      visible=False, key='pseudoLifetimeParam'))],
                    [sg.pin(sg.Column([[sg.Text('Driven distance until next pseudonym change [m]:', size=(45, 1)),
                                        sg.In(size=(10, 1), key='distanceIn', default_text=args.distance_threshold['default'],
                                              tooltip=self._tooltip(args.distance_threshold))]],
                                      visible=False, key='distanceParam'))],
                    [sg.pin(sg.Column([[sg.Text('SLOW Threshold [km/h]:', size=(20, 1)),
                                        sg.In(size=(10, 1), key='slowThresholdIn', default_text=args.slow_threshold['default'],
                                              tooltip=self._tooltip(args.slow_threshold))],
                                       [sg.Text('Time until next pseudonym change [sec]:', size=(35, 1)),
                                        sg.In(size=(10, 1), key='slowPseudoLifetimeIn', default_text=args.pseudonym_lifetime['default'],
                                              tooltip=self._tooltip(args.pseudonym_lifetime))]],
                                      visible=False, key='slowThresholdParam'))],
                    [sg.pin(sg.Column([[sg.Text('Road neighbor radius [m]:', size=(35, 1)),
                                        sg.In(size=(10, 1), key='whisperRoadNeighborRadiusIn',
                                              default_text=args.whisper_road_neighbor_radius['default'],
                                              tooltip=self._tooltip(args.whisper_road_neighbor_radius))],
                                       [sg.Text('General neighbor radius [m]:', size=(35, 1)),
                                        sg.In(size=(10, 1), key='whisperGeneralNeighborRadiusIn',
                                              default_text=args.whisper_general_neighbor_radius['default'],
                                              tooltip=self._tooltip(args.whisper_general_neighbor_radius))],
                                       [sg.Text('Close neighbor radius [m]:', size=(35, 1)),
                                        sg.In(size=(10, 1), key='whisperCloseNeighborRadiusIn',
                                              default_text=args.whisper_close_neighbor_radius['default'],
                                              tooltip=self._tooltip(args.whisper_close_neighbor_radius))],
                                       [sg.Text('Counter for pseudonym change trigger:', size=(35, 1)),
                                        sg.In(size=(10, 1), key='whisperCounterIn',
                                              default_text=args.whisper_counter['default'],
                                              tooltip=self._tooltip(args.whisper_counter))]],
                                      visible=False, key='whisperParam'))],
                    [sg.pin(sg.Column([[sg.Text('Number of neighbors for pseudo change:', size=(35, 1)),
                                        sg.In(size=(10, 1), key='cpnNeighborThresholdIn',
                                              default_text=args.cpn_neighbor_threshold['default'],
                                              tooltip=self._tooltip(args.cpn_neighbor_threshold))],
                                       [sg.Text('Radius to detect neighbors [m] :', size=(35, 1)),
                                        sg.In(size=(10, 1), key='cpnNeighborRadiusIn',
                                              default_text=args.cpn_neighbor_radius['default'],
                                              tooltip=self._tooltip(args.cpn_neighbor_radius))]],
                                      visible=False, key='cpnParam'))],
                    [sg.Text('Selection of additional Hardware options:', size=(60, 1)),
                     sg.Combo(values=list(HardwareType), key='hardwareOptionsCombo', default_value=args.hardware['default'],
                              tooltip=self._tooltip(args.hardware), readonly=True, enable_events=True)],
                    [sg.pin(sg.Column([[sg.Text('Vehicle ID with hardware connection:', size=(30, 1)),
                                        sg.In(size=(20, 1), key='hardwareVehId', default_text=args.hardware_veh_id['default'],
                                              tooltip=self._tooltip(args.hardware_veh_id))],
                                       [sg.Text('Local IP address of Hardware:', size=(30, 1)),
                                        sg.In(size=(20, 1), key='hwLocalIpIn', default_text=args.hardware_local_ip['default'],
                                              tooltip=self._tooltip(args.hardware_local_ip))],
                                       [sg.Text('Local Port of Hardware:', size=(30, 1)),
                                        sg.In(size=(20, 1), key='hwLocalPortIn', default_text=args.hardware_local_port['default'],
                                              tooltip=self._tooltip(args.hardware_local_port))],
                                       [sg.Text('Remote IP address of Hardware:', size=(30, 1)),
                                        sg.In(size=(20, 1), key='hwRemoteIpIn', default_text=args.hardware_remote_ip['default'],
                                              tooltip=self._tooltip(args.hardware_remote_ip))],
                                       [sg.Text('Remote Port address of Hardware:', size=(30, 1)),
                                        sg.In(size=(20, 1), key='hwRemotePortIn', default_text=args.hardware_remote_port['default'],
                                              tooltip=self._tooltip(args.hardware_remote_port))]],
                                      visible=False, key='hardwareParam'))]])],  # type: ignore

                [sg.Text('Starting Simulation ...', size=(55, 1), key='BarText', visible=False)],
                [sg.ProgressBar(max_value=100, size=(55, 30), key='LoadingBar', metadata=5, visible=False)],
                [sg.Button('Start', key='StartButton'), sg.Button('Cancel')],
                ]

    def change_scenario_generation_gui(self, value: bool, window):
        """Switches gui elements to disabled or enabled by value of radio element
        """

        window['scenarioPathIn'].update(disabled=value)
        window['scenarioPathBrowse'].update(disabled=value)

        window['scenarioOptionsCombo'].update(disabled=not value)
        window['spawnRateIn'].update(disabled=not value)
        window['sumoGuiOptionsCheckbox'].update(disabled=not value)
        window['loggingOptionsCheckbox'].update(disabled=not value)
        window['strategyOptionsCombo'].update(disabled=not value)
        window['hardwareOptionsCombo'].update(disabled=not value)
        window['pseudoOptionsCombo'].update(disabled=not value)
        window['simTimeIn'].update(disabled=not value)

    def change_pseudo_params_visibility(self, pseudo_change: PseudoChangeType, window):
        """Switches gui elements to visible or invisible by value of pseudo change value
        """

        window_elements = {
            PseudoChangeType.PERIODICAL: window['pseudoLifetimeParam'],
            PseudoChangeType.SLOW: window['slowThresholdParam'],
            PseudoChangeType.DISTANCE: window['distanceParam'],
            PseudoChangeType.WHISPER: window['whisperParam'],
            PseudoChangeType.CPN: window['cpnParam'],
        }

        for pcs, element in window_elements.items():
            if pcs == pseudo_change:
                element.update(visible=True)
            else:
                element.update(visible=False)

    def change_strategy_visibility(self, strategy: StrategyType, window):
        """Switches gui elements to visible or invisible by value of attacker strategy
        """

        if strategy == StrategyType.NO_ATTACKER:
            window['attackerParam'].update(visible=False)
        elif strategy == StrategyType.ATTACKER_SERVICE:
            window['attackerParam'].update(visible=True)

    def change_hardware_visibility(self, hardware_type: HardwareType, window):
        """Switches gui elements to visible or invisible by value of hardware configuration
        """
        if hardware_type == HardwareType.NONE:
            window['hardwareParam'].update(visible=False)
        elif hardware_type == HardwareType.COHDA:
            window['hardwareParam'].update(visible=True)

    def is_type(self, values: 'list[Any]', type: type) -> bool:
        """Returns True if all values are of a specific type (e.g. int, float..)
        """
        for value in values:
            try:
                type(value)
            except ValueError:
                return False

        return True

    def run_gui(self):
        """
            In this method lies the complexity of the gui.
            The window gets initialized and reacts afterwards on events,
            like value changes or click events.
        """

        # Create the Window
        window = sg.Window('V2X Simulation', self.create_layout(), finalize=True)
        window['LoadingBar'].Widget.config(mode='indeterminate')

        # Event Loop to process 'events' and get the 'values' of the inputs
        while True:
            event, values = window.read(timeout=100)
            close = self.handle_event(event, values, window)
            if close:
                break

            if self.error:
                self.running = False
                self.generating_finished = True
                self.error = False
                sg.popup_error(self.error_message, keep_on_top=True, title='Error')

            if self.generating_finished:
                self.running = False
                self.generating_finished = False
                window['StartButton'].update(disabled=False)
                window['LoadingBar'].update(visible=False)
                window['BarText'].update(visible=False)

            window['LoadingBar'].Widget['value'] += window['LoadingBar'].metadata

        window.close()

    def handle_event(self, event: str, values: 'dict[str, Any]', window: sg.Window) -> bool:
        """Handles the UI event.

        Args:
            event (str): Emitted event.
            values (dict[str, Any]): Input values.
            window (Window): UI window.

        Returns:
            bool: UI should exit.
        """
        if event is None or event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            return True
        # if user presses start start run function in another thread and let it generate all the files
        elif event == 'StartButton' and not self.running:
            self.handle_start(values, window)
        elif event == 'generateScenarioRadioTrue' or event == 'generateScenarioRadioFalse':
            self.change_scenario_generation_gui(values['generateScenarioRadioTrue'], window)
        elif event == 'pseudoOptionsCombo':
            self.change_pseudo_params_visibility(values['pseudoOptionsCombo'], window)
        elif event == 'hardwareOptionsCombo':
            self.change_hardware_visibility(values['hardwareOptionsCombo'], window)
        elif event == 'strategyOptionsCombo':
            self.change_strategy_visibility(values['strategyOptionsCombo'], window)

        return False

    def handle_start(self, values: 'dict[str, Any]', window: sg.Window):
        """Handle event when user presses start button.

        Args:
            values (dict[str, Any]): Input values.
            window (Window): UI window.
        """
        # Check if user input is ok
        if not (self.is_type([values['pseudoLifetimeIn'], values['slowThresholdIn'],
                              values['slowPseudoLifetimeIn'], values['spawnRateIn'],
                              values['spawnDelayIn'], values['distanceIn'],
                              values['whisperRoadNeighborRadiusIn'],
                              values['whisperGeneralNeighborRadiusIn'],
                              values['whisperCloseNeighborRadiusIn'],
                              values['cpnNeighborRadiusIn'], values['visualRangeIn']], float)
                and self.is_type([values['simTimeIn'], values['hwRemotePortIn'], values['hwLocalPortIn'],
                                  values['jobsIn'], values['seedIn'], values['whisperCounterIn'],
                                  values['cpnNeighborThresholdIn']], int)):

            self.error = True
            self.error_message = 'Input values are not correct.\nPlease Check the given values in the input fields'

            return

        cfg = self._get_config(values)

        # if generating files is activated run the generation method in another thread
        if values['generateScenarioRadioTrue']:
            thread = threading.Thread(target=self.generation_method, args=[cfg, self], daemon=True)
            thread.start()
        # else only start the simulation of the scenario
        else:
            thread = threading.Thread(target=self.simulation_method, args=[cfg.no_sumo_gui, cfg.simulate_scenario, self])
            thread.start()

        self.running = True

        window['StartButton'].update(disabled=True)
        window['LoadingBar'].update(visible=True)
        window['BarText'].update(visible=True)

    def _tooltip(self, arg: args.Argument) -> str:
        """
        Constructs a tooltip from an arguments help description
        either with or without default value included.

        Args:
            arg (Argument): Argument with help description.

        Returns:
            str: Tooltip which can be used in the GUI.
        """
        if 'default' in arg:
            return arg['help'] % {'default': arg['default']} # type: ignore

        return arg['help']


    def _get_config(self, values: 'dict[str, Any]') -> SimConfig:
        """Create config out of input values.

        Args:
            values (dict[str, Any]): Input values.

        Returns:
            SimConfig: Created config from input values.
        """

        is_slow = values['pseudoOptionsCombo'] == PseudoChangeType.SLOW
        pseudonym_lifetime = float(values['slowPseudoLifetimeIn'] if is_slow else values['pseudoLifetimeIn'])

        cfg = {
            # General
            args.scenario['key']: values['scenarioOptionsCombo'],
            args.spawn_rate['key']: float(values['spawnRateIn']),
            args.sim_time['key']: float(values['simTimeIn']),
            args.no_sumo_gui['key']: not values['sumoGuiOptionsCheckbox'],
            args.no_logging['key']: values['loggingOptionsCheckbox'],
            args.simulate_scenario['key']: values['scenarioPathIn'] or None, # If no input set None instead of empty string
            args.jobs['key']: int(values['jobsIn']),
            args.seed['key']: int(values['seedIn']),
            args.only_generation['key']: False,
            args.dry_run['key']: False,

            # Pseudonym change strategies
            args.pseudonym_change['key']: values['pseudoOptionsCombo'],
            args.pseudonym_lifetime['key']: pseudonym_lifetime,
            args.slow_threshold['key']: float(values['slowThresholdIn']),
            args.distance_threshold['key']: float(values['distanceIn']),
            args.whisper_road_neighbor_radius['key']: float(values['whisperRoadNeighborRadiusIn']),
            args.whisper_general_neighbor_radius['key']: float(values['whisperGeneralNeighborRadiusIn']),
            args.whisper_close_neighbor_radius['key']: float(values['whisperCloseNeighborRadiusIn']),
            args.whisper_counter['key']: int(values['whisperCounterIn']),
            args.cpn_neighbor_radius['key']: float(values['cpnNeighborRadiusIn']),
            args.cpn_neighbor_threshold['key']: int(values['cpnNeighborThresholdIn']),

            # Attacker
            args.strategy['key']: values['strategyOptionsCombo'],
            args.attacker_id['key']: values['attackerIdIn'] or None, # If no input set None instead of empty string
            args.target_id['key']: values['targetIdIn'] or None,     # If no input set None instead of empty string
            args.visual_range['key']: float(values['visualRangeIn']),
            args.spawn_delay['key']: float(values['spawnDelayIn']),

            # Hardware
            args.hardware['key']: values['hardwareOptionsCombo'],
            args.hardware_veh_id['key']: values['hardwareVehId'] or None, # If no input set None instead of empty string
            args.hardware_remote_ip['key']: values['hwRemoteIpIn'],
            args.hardware_remote_port['key']: int(values['hwRemotePortIn']),
            args.hardware_local_ip['key']: values['hwLocalIpIn'],
            args.hardware_local_port['key']: int(values['hwLocalPortIn']),
        }

        return SimConfig(cfg)
