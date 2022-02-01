from pathlib import Path
from typing import Dict, Tuple, Callable, List

import numpy as np
import pandas as pd
from timeeval import DatasetManager, TrainingType
from timeeval.adapters import DockerAdapter
from timeeval import Metric
from timeeval_experiments.algorithms import kmeans, torsk, dbstream, lstm_ad, normalizing_flows

from skopt import gp_minimize
from tempfile import TemporaryDirectory

from s2gpp import s2gpp, post_s2gpp

PostMethod = Callable[[np.ndarray, Dict], np.ndarray]
Method = Tuple[DockerAdapter, Dict, PostMethod]


def calculate_metric(post_method: PostMethod, args: Dict, dataset: Path) -> float:
    scores = np.genfromtxt(args["results_path"] / "docker-algorithm-scores.csv")
    scores = post_method(scores, args)
    labels = pd.read_csv(dataset).iloc[:, -1].values
    result = Metric.PR_AUC(labels, scores)
    return -result


def func(algorithm: DockerAdapter, post_method: PostMethod, dataset: Path, param_names: List[str], *params) -> float:
    try:
        with TemporaryDirectory(dir="./") as tmpdirname:
            result_file = Path(tmpdirname)
            print(result_file)
            args = {
                "results_path": result_file,
                "hyper_params": {
                    k: v for k, v in zip(param_names, params)
                }
            }
            print(f"Trying args: {args['hyper_params']}")
            algorithm(dataset, args)
            return calculate_metric(post_method, args, dataset)
    except:
        return 0.0


def hyperopt(dataset: Path, method: Method):
    algorithm, params, post_method = method
    param_names, params = zip(*params.items())

    result = gp_minimize(lambda p: func(algorithm, post_method, dataset, param_names, *p), params, n_calls=10)

    print(result)


def define_algorithms() -> List[Method]:
    return [
        (s2gpp(), {
            "pattern-length": (20, 150),
            "latent": (6, 50),
            "query-length": (30, 225),
            "rate": [100]
        }, post_s2gpp)
    ]


def define_datasets() -> List[Path]:
    dm = DatasetManager("../data/GutenTAG")
    return [dm.get_dataset_path(dataset_id) for dataset_id in dm.select(dataset="sinus-combined-diff-1.unsupervised")]


def main():
    algorithms = define_algorithms()
    datasets = define_datasets()

    for algorithm in algorithms:
        for dataset in datasets:
            hyperopt(dataset, algorithm)


if __name__ == '__main__':
    main()
