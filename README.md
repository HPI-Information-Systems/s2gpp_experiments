# S2G++ Experiments

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

## Run Hyper Opt

```shell
python -m hyperopt ...
```
