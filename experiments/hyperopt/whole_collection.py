from typing import List

import numpy as np
from skopt import gp_minimize
from timeeval.adapters import DockerAdapter
from tqdm import trange
import time

from ..algorithms import Method, PostMethod, Heuristics
from .base import BaseHyperopt
from ..utils import suppress_stdout_stderr, func


class WholeCollectionHyperopt(BaseHyperopt):
    def optimize(self):
        self.pb = trange(len(self.algorithms) * len(self.datasets) * self.n_calls)
        self.pb.update(self._count_results())
        time.sleep(1)
        for algorithm in self.algorithms:
            with suppress_stdout_stderr():
                try:
                    with suppress_stdout_stderr():
                        self._minimize(algorithm)
                except ValueError:
                    self.pb.write("Error occurred! Continue with next optimization")
                    self._add_error_entry(algorithm)

    def _minimize(self, method: Method):
        algorithm, params, post_method, heuristics = method
        param_names, params = zip(*params.items())

        result = gp_minimize(lambda p: self._call_heuristics(algorithm, post_method, param_names, heuristics, *p), params, n_calls=self.n_calls)

        self.results[algorithm.image_name]["whole-collection"]["score"] = -result["fun"]
        self.results[algorithm.image_name]["whole-collection"]["location"] = {n: int(x) if type(x) == np.int64 else x for n, x in zip(param_names, result["x"])}

    def _call_heuristics(self, algorithm: DockerAdapter, post_method: PostMethod, param_names: List[str], heuristics: Heuristics, *params) -> float:
        results = []

        for dataset in self.datasets:
            new_params = {
                name: p
                for name, p in zip(param_names, params)
            }
            for name, p in zip(param_names, params):
                new_params[name] = heuristics.get(name, lambda p, a: a[name])(dataset, new_params)

            res = func(algorithm, post_method, dataset, param_names, self.metric, *[new_params[n] for n in param_names])
            results.append(res)
            self.pb.update(1)

        return np.nanmedian(results).item()

    def _add_error_entry(self, algorithm: Method):
        self.results[algorithm[0].image_name]["whole-collection"]["score"] = None
        self.results[algorithm[0].image_name]["whole-collection"]["location"] = {}
