from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List

import numpy as np
import pandas as pd
from timeeval import Metric
from timeeval.adapters import DockerAdapter

from hyperopt import PostMethod


def calculate_metric(post_method: PostMethod, args: Dict, dataset: Path) -> float:
    scores = np.genfromtxt(args["results_path"] / "docker-algorithm-scores.csv")
    scores = post_method(scores, args)
    labels = pd.read_csv(dataset).iloc[:, -1].values
    result = Metric.PR_AUC(labels, scores)
    return -result


def func(algorithm: DockerAdapter, post_method: PostMethod, dataset: Path, param_names: List[str], *params) -> float:
    try:
        with TemporaryDirectory(dir="../") as tmpdirname:
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
