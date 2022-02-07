from pathlib import Path

import numpy as np
from tqdm import trange
import time, os

from ..algorithms import Method
from .base import BaseHyperopt
from ..utils import suppress_stdout_stderr


class NoHyperopt(BaseHyperopt):
    def optimize(self):
        pb = trange(len(self.algorithms) * len(self.datasets))
        pb.update(self._count_results())
        time.sleep(1)
        for algorithm in self.algorithms:
            for dataset in self.datasets:
                if self._combination_not_yet_done(algorithm, dataset):
                    try:
                        with suppress_stdout_stderr():
                            self._minimize(dataset, algorithm)
                    except ValueError:
                        pb.write("Error occurred! Continue with next optimization")
                        self._add_error_entry(algorithm, dataset)
                    pb.update(1)

    def _minimize(self, dataset: Path, method: Method):
        algorithm, params, post_method, heuristics = method
        param_names, params = zip(*params.items())
        params = [p[0] for p in params]
        result = -self._call_heuristics(algorithm, post_method, dataset, param_names, heuristics, *params)

        self.results[algorithm.image_name][str(dataset)]["score"] = result
        self.results[algorithm.image_name][str(dataset)]["location"] = [int(x) if type(x) == np.int64 else x for x in params]

    def _add_error_entry(self, algorithm: Method, dataset: os.PathLike):
        self.results[algorithm[0].image_name][str(dataset)]["score"] = None
        self.results[algorithm[0].image_name][str(dataset)]["location"] = []
