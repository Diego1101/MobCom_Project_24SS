# Pseudonym testing for V2X communication (Gen2)

This project aims to provide a simulation framework for testing pseudonym change procedures in V2X communication. 
It is the continuation of the [original project from WS21](https://gitlab.hs-esslingen.de/dschoop/mobcom_project_21ws) 
tasked with answering the question: Which pseudonym change strategy allow for the best privacy?

[TOC]

## Folder structure

The repository has the following high-level structure:

- `0_Orga` contains organizational information (e.g. project meeting protocols).
- `1_Literature` contains all bibliographic information (e.g. literature management).
- `2_Documentation` contains documentation related files. The project documentation is available in the [GitLab-Wiki](https://gitlab.hs-esslingen.de/dschoop/mobcom_project_22ws/-/wikis/home).
- `3_Presentation` contains the midterm and final presentations of the project.
- `4_Code` contains the source code of the project.

## Requirements & Installation

This repository already includes a fork of the [Artery framework](http://artery.v2x-research.eu/) on which this project is based. Linux is the expected platform (requirement of Artery). A detailed guide on what requirements are needed and how to install everything can be found in the Wiki in chapter [Simulation Environment](https://gitlab.hs-esslingen.de/dschoop/mobcom_project_22ws/-/wikis/home#2-simulation-environment).

The framework and simulation is built automatically when a new simulation run is started via the main run script. If one wishes to build the framework explicitly, one may execute the shell script `build_project.sh` under `4_Code/scripts/bash`. Beware that the first simulation run can take a long time to get started because everything needs to be compiled first.

## Running a simulation

A detailed guide can be found in the [Wiki](https://gitlab.hs-esslingen.de/dschoop/mobcom_project_22ws/-/wikis/4.-Implementation/4.1-Simulation-Control/4.1.1-Simulation-Pipeline).

To start a simulation run execute:
```bash
cd 4_Code/scripts/python
python3 run.py
```
You will be presented with a GUI with possible configuration options.

You can also run a simulation by using command line arguments, like for example:
```bash
cd 4_Code/scripts/python
python3 run.py -s esslingen_extension -r 10 -t 180 -p periodical --no-sumo-gui --no-logging 
```
Running the simulation in console is the recommended approach as it will provide you with the best performance.

To see all arguments, go to the [Wiki page](https://gitlab.hs-esslingen.de/dschoop/mobcom_project_22ws/-/wikis/4.-Implementation/4.1-Simulation-Control/4.1.1-Simulation-Pipeline) or type in the console: 
```bash
python3 run.py -h
```

## Evaluating the simulation

The `run.py` only runs the simulation and does no evaluation on the resulting data.
To analyze and evaluate the data, use the `evaluate.py` script in the `4_Code/scripts/python` folder.

The `evaluate.py` script requires the path to the result folder of your simulation run.
This folder can be found in the `4_Code/scenarios` directory or is printed at the end of a simulation run.

*Example:* Evaluate scenario based on static (`-s`) and dynamic (`-d`) attacker models. Return the degree of anonymity (`-a`) and pseudonym consumption (`-c`).
```bash
cd 4_Code/scripts/python
python3 evaluate.py ../../scenarios/esslingen_extension/strat=no_service+pcs=periodical+traffic=10.0+t=180 -s -d -a -c
```

To see all arguments, go to the [Wiki page](https://gitlab.hs-esslingen.de/dschoop/mobcom_project_22ws/-/wikis/4.-Implementation/4.1-Simulation-Control/4.1.1-Simulation-Pipeline) or type in the console: 
```bash
python3 evaluate.py -h
```

## Further information

More information may be found in the [GitLab-Wiki](https://gitlab.hs-esslingen.de/dschoop/mobcom_project_22ws/-/wikis/home), providing an extensive, detailed documentation.
