# Simulation scripts

## Requirements

Use Python >= 3.7 and install all requirements using following command:
```bash
pip3 install -r requirements.txt
```

## Simulate

To start a simulation run execute:
```bash
python3 run.py
```
You will be presented with a GUI with possible configuration options.

You can also run a simulation by using command line arguments, like for example:
```bash
python3 run.py -s esslingen_extension -r 10 -t 180 -p periodical --pseudonym-lifetime 10 --no-sumo-gui --no-logging 
```
Running the simulation in console is the recommended approach as it will provide you with the best performance.

To see all arguments, type: 
```bash
python3 run.py -h
```

## Evaluate

The `run.py` only runs the simulation and does no evaluation on the resulting data.
To analyze and evaluate the data, use the `evaluate.py` script.

The `evaluate.py` script requires the path to the result folder of your simulation run.
This folder can be found in the `scenarios` directory or is printed at the end of a simulation run.

*Example:* Evaluate scenario based on static (`-s`) and dynamic (`-d`) attacker models. Return the degree of anonymity (`-a`) and pseudonym consumption (`-c`).
```bash
python3 evaluate.py ../../scenarios/esslingen_extension/strat=no_service+pcs=periodical+traffic=10.0+t=180 -s -d -a -c
```

To see all arguments, type: 
```bash
python3 evaluate.py -h
```
