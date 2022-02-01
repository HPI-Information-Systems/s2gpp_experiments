from typing import Callable, Dict, Tuple, List

import numpy as np
from timeeval.adapters import DockerAdapter
from .s2gpp import s2gpp, post_s2gpp
from .kmeans import kmeans, post_kmeans
from .torsk import torsk, _post_torsk
from .dbstream import dbstream, post_dbstream

PostMethod = Callable[[np.ndarray, Dict], np.ndarray]
Method = Tuple[DockerAdapter, Dict, PostMethod]


def define_algorithms(filters: List[str]) -> List[Method]:
    algorithms = [
        (s2gpp(), {
            "pattern-length": (20, 150),
            "latent": (6, 50),
            "query-length": (30, 225),
            "rate": [100]
        }, post_s2gpp),

        (kmeans(), {
            "anomaly_window_size": (20, 150),
            "n_clusters": (5, 50),
            "stride": (1, 20)
        }, post_kmeans)
    ]

    if len(filters) > 0:
        algorithms = list(filter(lambda a: a[0].image_name in filters, algorithms))

    return algorithms
