import time

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
    def __init__(self, algorithms: List[Method], datasets: List[Path], n_calls: int = 10, verbose: bool = False, metric: Metric = Metric.ROC_AUC, results_path: Optional[Path] = None):
        self.algorithms: List[Method] = algorithms
        self.datasets: List[Path] = datasets
        self.n_calls = n_calls
        self.verbose = verbose
        self.metric = metric
        self.results: DefaultDict[str, DefaultDict[str, Dict[str, Union[Optional[float], List[Any]]]]] = defaultdict(lambda: defaultdict(dict))
        if results_path is not None:
            self._load_finished_results(results_path)

    def optimize(self):
        pb = tqdm.trange(len(self.algorithms) * len(self.datasets))
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

    def _load_finished_results(self, results_path: Path):
        with results_path.open("r") as f:
            finished_results = json.load(f)
        for algorithm, datasets in finished_results.items():
            for dataset, props in datasets.items():
                self.results[algorithm][dataset]["score"] = props["score"]
                self.results[algorithm][dataset]["location"] = props["location"]

    def _combination_not_yet_done(self, algorithm: Method, dataset: Path) -> bool:
        algorithm_name = algorithm[0].image_name
        if algorithm_name in self.results:
            if str(dataset) in self.results[algorithm_name]:
                return False
        return True

    def _count_results(self) -> int:
        count = 0
        for _algorithm, datasets in self.results.items():
            count += len(datasets)
        return count

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
