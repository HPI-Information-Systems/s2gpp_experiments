# S2G++ Experiments

This repository holds the experiment definitions for the _Series2Graph++_ paper. 
The code for the algorithm can be found [here](https://github.com/HPI-Information-Systems/S2Gpp).

The following experiments can be reproduced:

- [Quality](#Quality Experiment)
- Correlation Anomaly Detection
- Self-Correction
- Scalability
- Explainability
- Hyper-Parameter Optimization

## Requirements

- Python 3
- GutenTAG (will be installed with this repository)
- TimeEval (will be installed with this repository)
- Docker

## Installation

```shell
python setup.py install
```


## Build Docker Images

Uses images from [TimeEval-Algorithms repository](https://github.com/HPI-Information-Systems/TimeEval-algorithms).

```shell
./build-images.sh
```


## Generate Datasets

```shell
python -m gutentag ...
```

# Quality Experiment

For this experiment, we use the [TimeEval](https://github.com/HPI-Information-Systems/TimeEval) evaluation 
tool with the script in [haystack-experiment.py](experiment_scripts/haystack-experiment.py). 
If you want to repeat this experiment on your machines, be aware to change the remote machines to your addresses in [this part of the script](experiment_scripts/haystack-experiment.py#L238) 

```shell
python experiment_scripts/haystack-experiment.py
```

# Correlation Anomaly Detection Experiment

For this experiment, we use the [TimeEval](https://github.com/HPI-Information-Systems/TimeEval) evaluation 
tool with the script in [comut-experiment.py](experiment_scripts/comut-experiment.py). 
If you want to repeat this experiment on your machines, be aware to change the remote machines to your addresses in [this part of the script](experiment_scripts/comut-experiment.py#L237) 

```shell
python experiment_scripts/comut-experiment.py
```

# Self-Correction Experiment

For this experiment, we use the [TimeEval](https://github.com/HPI-Information-Systems/TimeEval) evaluation 
tool with the script in [self-correction-experiment.py](experiment_scripts/self-correction-experiment.py). 
If you want to repeat this experiment on your machines, be aware to change the remote machines to your addresses in [this part of the script](experiment_scripts/self-correction-experiment.py#L241) 

```shell
python experiment_scripts/self-correction-experiment.py
```

# Scalability Experiment

For this experiment, we use the [TimeEval](https://github.com/HPI-Information-Systems/TimeEval) evaluation 
tool with the scripts in [scalability-experiment.py](experiment_scripts/scalability-experiment.py) and [scalability-xl-experiment.py](experiment_scripts/scalability-xl-experiment.py). 
If you want to repeat this experiment on your machines, be aware to change the remote machines to your addresses in [this part of the script](experiment_scripts/scalability-experiment.py#L264) and [this part of the other script](experiment_scripts/scalability-xl-experiment.py#L259).

```shell
python experiment_scripts/scalability-experiment.py
python experiment_scripts/scalability-xl-experiment.py
```

# Explainability Experiment

For this experiment, we do not use TimeEval. The script in [explainability-experiment.py](experiment_scripts/explainability-experiment.py) performs the experiment.
If you want to repeat this experiment on your machines, be aware to adapt the local docker image name [here](experiment_scripts/explainability-experiment.py#L25) and group [here](experiment_scripts/explainability-experiment.py#L119) that you have built before.

```shell
python experiment_scripts/explainability-experiment.py
```

# Hyper-Parameter Optimization

For this experiment, we do not use TimeEval. The scripts in [experiments/hyperopt](experiments/hyperopt) perform the optimization.
If you want to repeat this experiment on your machines, be aware to adapt the local docker image name [here](experiments/algorithms/s2gpp.py).

```shell
python -m hyperopt --algorithms <image-name> --hyperopt-calls 30 --training-type unsupervised --output-file results.json --dataset-dir data/hyperopt --mode whole_collection
```

# TODO

- [ ] update param-config paths
