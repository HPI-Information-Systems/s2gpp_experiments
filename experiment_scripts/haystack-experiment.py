#!/usr/bin/env python3
import logging
import random
import shutil
import sys
from typing import List, Tuple, Dict, Any, Optional

import numpy as np
from durations import Duration

from timeeval import TimeEval, DatasetManager, Algorithm, TrainingType, InputDimensionality
from timeeval.adapters import DockerAdapter
from timeeval.constants import HPI_CLUSTER
from timeeval.params import FixedParameters, ParameterConfig
from timeeval.remote import RemoteConfiguration
from timeeval.resource_constraints import ResourceConstraints, GB
from timeeval.utils.metrics import Metric
from timeeval.utils.window import ReverseWindowing
from timeeval_experiments.algorithm_configurator import AlgorithmConfigurator
from timeeval_experiments.algorithms import *


"""
############## mSTAMP
"""

def post_mstamp(scores: np.ndarray, args: dict) -> np.ndarray:
    window_size = args.get("hyper_params", {}).get("anomaly_window_size", 50)
    return ReverseWindowing(window_size=window_size).fit_transform(scores)


_mstamp_parameters: Dict[str, Dict[str, Any]] = {
    "anomaly_window_size": {
        "defaultValue": 30,
        "description": "Size of the sliding window.",
        "name": "anomaly_window_size",
        "type": "Int"
    },
    "random_state": {
        "defaultValue": 42,
        "description": "Seed for random number generation.",
        "name": "random_state",
        "type": "Int"
    }
}


def mstamp(params: ParameterConfig = None, skip_pull: bool = False, timeout: Optional[Duration] = None) -> Algorithm:
    return Algorithm(
        name="mSTAMP",
        main=DockerAdapter(
            image_name="sopedu:5000/akita/mstamp",
            skip_pull=skip_pull,
            timeout=timeout,
            group_privileges="akita",
        ),
        preprocess=None,
        postprocess=post_mstamp,
        param_schema=_mstamp_parameters,
        param_config=params or ParameterConfig.defaults(),
        data_as_file=True,
        training_type=TrainingType.UNSUPERVISED,
        input_dimensionality=InputDimensionality("multivariate")
    )


"""
############## s2gpp
"""

def post_s2gpp(scores: np.ndarray, args: dict) -> np.ndarray:
    pattern_length = args.get("hyper_params", {}).get("pattern-length", 50)
    query_length = args.get("hyper_params", {}).get("query-length", 75)
    size = pattern_length + query_length
    return ReverseWindowing(window_size=size).fit_transform(scores)


_s2gpp_parameters: Dict[str, Dict[str, Any]] = {
    "pattern-length": {
        "name": "pattern-length",
        "type": "Int",
        "defaultValue": 50,
        "description": "Size of the sliding window, independent of anomaly length, but should in the best case be larger."
    },
    "latent": {
        "name": "latent",
        "type": "Int",
        "defaultValue": 16,
        "description": "Size of latent embedding space. This space is the input for the PCA calculation afterwards."
    },
    "rate": {
        "name": "rate",
        "type": "Int",
        "defaultValue": 100,
        "description": "Number of angles used to extract pattern nodes. A higher value will lead to high precision, but at the cost of increased computation time."
    },
    "threads": {
        "name": "threads",
        "type": "Int",
        "defaultValue": 1,
        "description": "Number of helper threads started besides the main thread. (min=1)"
    },
    "query-length": {
        "name": "query-length",
        "type": "Int",
        "defaultValue": 75,
        "description": "Size of the sliding windows used to find anomalies (query subsequences). query-length must be >= pattern-length!"
    },
    "clustering": {
        "name": "clustering",
        "type": "String",
        "defaultValue": "meanshift",
        "description": "Determines which clustering algorithm to use. Possible choices are: `meanshift` or `kde`."
    }
}


def s2gpp_timeeval(name: str, params: ParameterConfig = None, skip_pull: bool = False, timeout: Optional[Duration] = None) -> Algorithm:
    return Algorithm(
        name=name,
        main=DockerAdapter(
            image_name="sopedu:5000/akita/s2gpp",
            tag="0.8.0",
            skip_pull=skip_pull,
            timeout=timeout,
            group_privileges="akita",
        ),
        preprocess=None,
        postprocess=post_s2gpp,
        param_schema=_s2gpp_parameters,
        param_config=params or ParameterConfig.defaults(),
        data_as_file=True,
        training_type=TrainingType.UNSUPERVISED,
        input_dimensionality=InputDimensionality("multivariate")
    )



logging.basicConfig(
    filename="timeeval.log",
    filemode="a",
    level=logging.INFO,
    # force=True,
    format="%(asctime)s %(levelname)6.6s - %(name)20.20s: %(message)s",
)

random.seed(42)
np.random.rand(42)
MAX_CONTAMINATION = 0.1
MIN_ANOMALIES = 1


def until_length_width(max_length: int, max_width: int, dataset: Tuple[str, str]) -> bool:
    dataset_name = dataset[1].split(".")[0]
    length, width = dataset_name.split("-")[1:]
    return int(length) <= max_length and int(width) <= max_width


def from_length_width(min_length: int, min_width: int, dataset: Tuple[str, str]) -> bool:
    dataset_name = dataset[1].split(".")[0]
    length, width = dataset_name.split("-")[1:]
    return int(length) >= min_length and int(width) >= min_width


def from_length(min_length: int, dataset: Tuple[str, str]) -> bool:
    dataset_name = dataset[1].split(".")[0]
    length, _width = dataset_name.split("-")[1:]
    return int(length) >= min_length


def until_width(max_width: int, dataset: Tuple[str, str]) -> bool:
    dataset_name = dataset[1].split(".")[0]
    _length, width = dataset_name.split("-")[1:]
    return int(width) <= max_width


def from_width(min_width: int, dataset: Tuple[str, str]) -> bool:
    dataset_name = dataset[1].split(".")[0]
    _length, width = dataset_name.split("-")[1:]
    return int(width) >= min_width


def main():
    dm = DatasetManager("/home/phillip.wenig/datasets/timeseries/haystack", create_if_missing=False)
    configurator = AlgorithmConfigurator(config_path="/home/phillip.wenig/projects/timeeval/timeeval_experiments/param-config.json")

    # Select datasets and algorithms
    datasets: List[Tuple[str, str]] = [d for d in dm.select()]
    print(f"Selecting {len(datasets)} datasets")

    algorithms = [
        s2gpp_timeeval(
            "S2G++20p-KDE",
            params=FixedParameters({
                "rate": 100,
                "pattern-length": "heuristic:AnomalyLengthHeuristic(agg_type='max')",
                "latent": "heuristic:ParameterDependenceHeuristic(source_parameter='pattern-length', factor=1./3.)",
                "query-length": "heuristic:ParameterDependenceHeuristic(source_parameter='pattern-length', factor=1.0)",
                "threads": 20,
                "clustering": "kde"
            }),
            skip_pull=True
        ),
        mstamp(
            params=FixedParameters({
                "anomaly_window_size": "heuristic:AnomalyLengthHeuristic(agg_type='max')"
            })
        ),
        dbstream(),
        kmeans(),
        lstm_ad(),
        normalizing_flows(),
        torsk(),
    ]
    print(f"Selecting {len(algorithms)} algorithms")

    print("Configuring algorithms...")
    configurator.configure(algorithms[2:], perform_search=False)

    print("\nDatasets:")
    print("=====================================================================================")
    for collection in np.unique([c for (c, d) in datasets]):
        print(collection)
        cds = sorted([d for (c, d) in datasets if c == collection])
        for cd in cds:
            print(f"  {cd}")
    print("=====================================================================================\n\n")

    print("\nParameter configurations:")
    print("=====================================================================================")
    for algo in algorithms:
        print(algo.name)
        for param in algo.param_config:
            print(f"  {param}")
    print("=====================================================================================\n\n")
    sys.stdout.flush()

    cluster_config = RemoteConfiguration(
        scheduler_host=HPI_CLUSTER.odin01,
        worker_hosts=[f"odin{i:02d}" for i in range(3,15)]
    )
    limits = ResourceConstraints(
        tasks_per_host=1,
        task_memory_limit=20*GB,
        train_timeout=Duration("2 hours"),
        execute_timeout=Duration("2 hours"),
    )
    timeeval = TimeEval(dm, datasets, algorithms,
                        repetitions=1,
                        distributed=True,
                        remote_config=cluster_config,
                        resource_constraints=limits,
                        force_training_type_match=True,
                        metrics=[Metric.ROC_AUC, Metric.PR_AUC, Metric.RANGE_PR_AUC, Metric.AVERAGE_PRECISION],
                        )

    # copy parameter configuration file to results folder
    timeeval.results_path.mkdir(parents=True, exist_ok=True)
    shutil.copy2(configurator.config_path, timeeval.results_path)

    timeeval.run()
    print(timeeval.get_results(aggregated=True, short=True))


if __name__ == "__main__":
    main()
