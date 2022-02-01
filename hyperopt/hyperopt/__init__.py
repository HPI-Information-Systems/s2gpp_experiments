import numpy as np
from pathlib import Path
from typing import List, Dict, Union, Any, DefaultDict
from .algorithms import Method, PostMethod
from skopt import gp_minimize
from collections import defaultdict
import json

from .utils import func


class Hyperopt:
    def __init__(self, algorithms: List[Method], datasets: List[Path], n_calls: int = 10):
        self.algorithms: List[Method] = algorithms
        self.datasets: List[Path] = datasets
        self.n_calls = n_calls
        self.results: DefaultDict[str, DefaultDict[str, Dict[str, Union[float, List[Any]]]]] = defaultdict(lambda: defaultdict(dict))

    def optimize(self):
        for algorithm in self.algorithms:
            for dataset in self.datasets:
                self._minimize(dataset, algorithm)

    def _minimize(self, dataset: Path, method: Method):
        algorithm, params, post_method = method
        param_names, params = zip(*params.items())

        result = gp_minimize(lambda p: func(algorithm, post_method, dataset, param_names, *p), params, n_calls=self.n_calls)

        self.results[algorithm.image_name][str(dataset)]["score"] = -result["fun"]
        self.results[algorithm.image_name][str(dataset)]["location"] = [int(x) if type(x) == np.int64 else x for x in result["x"]]

    def save_to_file(self, path: Path):
        with path.open("w") as f:
            json.dump(self.results, f)
