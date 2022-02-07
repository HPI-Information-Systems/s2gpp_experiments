from pathlib import Path
from typing import Callable, Dict, Tuple, List, Any

import numpy as np
from timeeval.adapters import DockerAdapter
from .s2gpp import s2gpp, post_s2gpp
from .kmeans import kmeans, post_kmeans
from .torsk import torsk, _post_torsk
from .dbstream import dbstream, post_dbstream
from ..heuristics import Heuristic
from ..heuristics.dataset_attr import DatasetAttrHeuristic
from ..heuristics.sibling import SiblingHeuristic

PostMethod = Callable[[np.ndarray, Dict], np.ndarray]
Heuristics = Dict[str, Heuristic]
Method = Tuple[DockerAdapter, Dict, PostMethod, Heuristics]


def define_algorithms(filters: List[str], dataset_dir: Path) -> List[Method]:
    algorithms = [
        (s2gpp(), {
            "pattern-length": (0.1, 5.0),
            "latent": (0.01, 1.0),
            "query-length": [1.5],
            "rate": [100]
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
