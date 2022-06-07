from contextlib import contextmanager, redirect_stderr, redirect_stdout
from os import devnull
from pathlib import Path
import random
from tempfile import TemporaryDirectory
from typing import List, Optional, Dict

import numpy as np
import pandas as pd
from timeeval import TrainingType, InputDimensionality, DatasetManager, Metric
from timeeval.adapters import DockerAdapter


def define_datasets(filters: List[Path], dataset_dir: Path, training_type: Optional[TrainingType] = None, input_dimensionality: Optional[InputDimensionality] = None, sample_n: Optional[int] = None) -> List[Path]:
    dm = DatasetManager(dataset_dir)
    datasets = [dm.get_dataset_path(dataset_id) for dataset_id in dm.select(training_type=training_type, input_dimensionality=input_dimensionality)]

    if len(filters) > 0:
        datasets = list(filter(lambda d: d.parent.name in filters, datasets))

    if sample_n is not None:
        datasets = random.choices(datasets, k=sample_n)

    return datasets


@contextmanager
def suppress_stdout_stderr():
    """A context manager that redirects stdout and stderr to devnull"""
    with open(devnull, 'w') as fnull:
        with redirect_stderr(fnull) as err, redirect_stdout(fnull) as out:
            yield (err, out)


def calculate_metric(post_method: 'PostMethod', args: Dict, dataset: Path, metric: Metric) -> float:
    scores = np.genfromtxt(args["results_path"] / "docker-algorithm-scores.csv")
    scores = post_method(scores, args)
    labels = pd.read_csv(dataset).iloc[:, -1].values
    result = metric(labels, scores)
    return result


def run_docker_algorithm(algorithm: DockerAdapter, dataset: Path, result_file: Path, params: Dict) -> Dict:
    args = {
        "results_path": result_file,
        "hyper_params": params
    }
    print(args, dataset)
    algorithm(dataset, args)
    return args


def func(algorithm: DockerAdapter, post_method: 'PostMethod', dataset: Path, param_names: List[str], metric: Metric, *params) -> float:
    try:
        with TemporaryDirectory(dir=".") as tmpdirname:
            result_file = Path(".") 
            params = dict(zip(param_names, params))
            args = run_docker_algorithm(algorithm, dataset, result_file, params)
        return -calculate_metric(post_method, args, dataset, metric)
    except:
        return 0.0
