import numpy as np
from pathlib import Path
from typing import List, Dict, Union, Any, DefaultDict, Optional

from timeeval import Metric

from .algorithms import Method, PostMethod
from skopt import gp_minimize
from collections import defaultdict
import json
import tqdm

from .utils import func, suppress_stdout_stderr


class Hyperopt:
    def __init__(self, algorithms: List[Method], datasets: List[Path], n_calls: int = 10, verbose: bool = False, metric: Metric = Metric.ROC_AUC):
        self.algorithms: List[Method] = algorithms
        self.datasets: List[Path] = datasets
        self.n_calls = n_calls
        self.verbose = verbose
        self.metric = metric
        self.results: DefaultDict[str, DefaultDict[str, Dict[str, Union[Optional[float], List[Any]]]]] = defaultdict(lambda: defaultdict(dict))

    def optimize(self):
        pb = tqdm.trange(len(self.algorithms) * len(self.datasets))
        for algorithm in self.algorithms:
            for dataset in self.datasets:
                try:
                    with suppress_stdout_stderr():
                        self._minimize(dataset, algorithm)
                except ValueError:
                    pb.write("Error occurred! Continue with next optimization")
                    self._add_error_entry(algorithm, dataset)
                pb.update(1)

    def _minimize(self, dataset: Path, method: Method):
        algorithm, params, post_method = method
        param_names, params = zip(*params.items())

        result = gp_minimize(lambda p: func(algorithm, post_method, dataset, param_names, self.metric, *p), params, n_calls=self.n_calls)

        self.results[algorithm.image_name][str(dataset)]["score"] = -result["fun"]
        self.results[algorithm.image_name][str(dataset)]["location"] = [int(x) if type(x) == np.int64 else x for x in result["x"]]

    def _add_error_entry(self, algorithm: Method, dataset: Path):
        self.results[algorithm[0].image_name][str(dataset)]["score"] = None
        self.results[algorithm[0].image_name][str(dataset)]["location"] = []

    def save_to_file(self, path: Path):
        with path.open("w") as f:
            json.dump(self.results, f)
