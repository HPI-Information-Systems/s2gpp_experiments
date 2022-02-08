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
    s2gpp_params = get_hyperopt_params()
    algorithms = [
        (s2gpp(), {
            "pattern-length": [s2gpp_params[0]],
            "latent": [s2gpp_params[1]],
            "query-length": [s2gpp_params[2]],
            "rate": [s2gpp_params[3]]
        }, post_s2gpp, {
            "pattern-length": DatasetAttrHeuristic(dataset_dir, attr="period_size", param="pattern-length", dtype=int),
            "latent": SiblingHeuristic(dataset_dir, sibling="pattern-length", param="latent", dtype=int),
            "query-length": SiblingHeuristic(dataset_dir, sibling="pattern-length", param="query-length", dtype=int)
        }),

        (kmeans(), {
            "anomaly_window_size": (20, 150),
            "n_clusters": (5, 50),
            "stride": (1, 20)
        }, post_kmeans, {})
    ]

    if len(filters) > 0:
        algorithms = list(filter(lambda a: a[0].image_name in filters, algorithms))

    return algorithms
