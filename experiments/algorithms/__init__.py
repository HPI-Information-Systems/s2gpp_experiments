from pathlib import Path
from typing import Callable, Dict, Tuple, List

import numpy as np
from timeeval.adapters import DockerAdapter
from .s2gpp import s2gpp, post_s2gpp, get_hyperopt_params
from .kmeans import kmeans, post_kmeans
from .dbstream import dbstream, post_dbstream
from experiments.heuristics import Heuristic
from experiments.heuristics.dataset_attr import DatasetAttrHeuristic
from experiments.heuristics.sibling import SiblingHeuristic

PostMethod = Callable[[np.ndarray, Dict], np.ndarray]
Heuristics = Dict[str, Heuristic]
Method = Tuple[DockerAdapter, Dict, PostMethod, Heuristics]


def define_algorithms(filters: List[str], dataset_dir: Path) -> List[Method]:
    algorithms = [
        (s2gpp(), {
            "pattern-length": [1],
            "latent": [0.2, 0.25, 0.33, 0.5],
            "query-length": [1.0, 1.5, 2.0, 2.5],
            "rate": [30, 50, 70, 100],
            "clustering": ["kde"],
            "threads": [8]
        }, post_s2gpp, {
            "pattern-length": DatasetAttrHeuristic(dataset_dir, attr="max_anomaly_length", param="pattern-length", dtype=int),
            "latent": SiblingHeuristic(dataset_dir, sibling="pattern-length", param="latent", dtype=int),
            "query-length": SiblingHeuristic(dataset_dir, sibling="pattern-length", param="query-length", dtype=int)
        }),
    ]

    if len(filters) > 0:
        algorithms = list(filter(lambda a: a[0].image_name in filters, algorithms))

    return algorithms
