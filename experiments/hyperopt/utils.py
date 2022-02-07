from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from os import devnull

import numpy as np
import pandas as pd
from timeeval import Metric
from timeeval.adapters import DockerAdapter

from ..algorithms import PostMethod


def calculate_metric(post_method: PostMethod, args: Dict, dataset: Path, metric: Metric) -> float:
    scores = np.genfromtxt(args["results_path"] / "docker-algorithm-scores.csv")
    scores = post_method(scores, args)
    labels = pd.read_csv(dataset).iloc[:, -1].values
    result = metric(labels, scores)
    return -result


def func(algorithm: DockerAdapter, post_method: PostMethod, dataset: Path, param_names: List[str], metric: Metric, *params) -> float:
    try:
        with TemporaryDirectory(dir="../") as tmpdirname:
            result_file = Path(tmpdirname)
            args = {
                "results_path": result_file,
                "hyper_params": {
                    k: v for k, v in zip(param_names, params)
                }
            }
            print(f"Trying args: {args['hyper_params']}")
            algorithm(dataset, args)
            return calculate_metric(post_method, args, dataset, metric)
    except:
        return 0.0


@contextmanager
def get_stdout(buf: StringIO):
    """A context manager that redirects stdout and stderr to devnull"""
    with open(devnull, 'w') as fnull:
        with redirect_stderr(fnull) as err, redirect_stdout(buf) as out:
            yield (err, out)
