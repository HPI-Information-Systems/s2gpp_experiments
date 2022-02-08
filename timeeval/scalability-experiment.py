#!/usr/bin/env python3
import logging
import random
import shutil
import sys
from typing import List, Tuple

import numpy as np
from durations import Duration

from timeeval import TimeEval, Datasets, TrainingType
from timeeval.constants import HPI_CLUSTER
from timeeval.params import FixedParameters
from timeeval.remote import RemoteConfiguration
from timeeval.resource_constraints import ResourceConstraints, GB
from timeeval.utils.metrics import Metric
from timeeval_experiments.algorithm_configurator import AlgorithmConfigurator
from timeeval_experiments.algorithms import *


# Setup logging
from experiments.algorithms.mstamp import mstamp
from experiments.algorithms.s2gpp import s2gpp_timeeval

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


def main():
    dm = Datasets("/home/phillip.wenig/Datasets/timeseries/scalability", create_if_missing=False)
    configurator = AlgorithmConfigurator(config_path="param-config.json")

    # Select datasets and algorithms
    datasets: List[Tuple[str, str]] = [d for d in dm.select() if d[1] == "ecg-10000-1"]
    print(f"Selecting {len(datasets)} datasets")

    algorithms = [
        s2gpp_timeeval(
            "S2G++1p",
            params=FixedParameters({
                "rate": 100,
                "pattern-length": "heuristic:PeriodSizeHeuristic(factor=1.0, fb_value=50)",
                "latent": "heuristic:ParameterDependenceHeuristic(source_parameter='pattern-length', factor=1./3.)",
                "query-length": "heuristic:ParameterDependenceHeuristic(source_parameter='pattern-length', factor=1.5)",
                "threads": 1
            })
        ),
        s2gpp_timeeval(
            "S2G++20p",
            params=FixedParameters({
                "rate": 100,
                "pattern-length": "heuristic:PeriodSizeHeuristic(factor=1.0, fb_value=50)",
                "latent": "heuristic:ParameterDependenceHeuristic(source_parameter='pattern-length', factor=1./3.)",
                "query-length": "heuristic:ParameterDependenceHeuristic(source_parameter='pattern-length', factor=1.5)",
                "threads": 20
            })
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
    configurator.configure(algorithms[3:], perform_search=False)

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
        worker_hosts=HPI_CLUSTER.nodes
    )
    limits = ResourceConstraints(
        tasks_per_host=1,
        task_memory_limit=20*GB,
        train_fails_on_timeout=False,
        train_timeout=Duration("1 hour"),
        execute_timeout=Duration("8 hours"),
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
