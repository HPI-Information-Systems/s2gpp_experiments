import abc
from collections import defaultdict
from pathlib import Path
from typing import List, Any, Optional, Union, Dict, DefaultDict

from timeeval import Metric
from timeeval.adapters import DockerAdapter

from .utils import func
import json


class BaseHyperopt(abc.ABC):
    def __init__(self, algorithms: List['Method'], datasets: List[Path], n_calls: int = 10, verbose: bool = False, metric: Metric = Metric.ROC_AUC, results_path: Optional[Path] = None):
        self.algorithms: List['Method'] = algorithms
        self.datasets: List[Path] = datasets
        self.n_calls = n_calls
        self.verbose = verbose
        self.metric = metric
        self.results: DefaultDict[str, DefaultDict[str, Dict[str, Union[Optional[float], List[Any]]]]] = defaultdict(lambda: defaultdict(dict))
        if results_path is not None:
            self._load_finished_results(results_path)

    @abc.abstractmethod
    def optimize(self):
        ...

    def _load_finished_results(self, results_path: Path):
        with results_path.open("r") as f:
            finished_results = json.load(f)
        for algorithm, datasets in finished_results.items():
            for dataset, props in datasets.items():
                self.results[algorithm][dataset]["score"] = props["score"]
                self.results[algorithm][dataset]["location"] = props["location"]

    def _combination_not_yet_done(self, algorithm: 'Method', dataset: Path) -> bool:
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

    def _call_heuristics(self, algorithm: DockerAdapter, post_method: 'PostMethod', dataset: Path, param_names: List[str], heuristics: 'Heuristics', *params) -> float:
        new_params = {
            name: p
            for name, p in zip(param_names, params)
        }
        for name, p in zip(param_names, params):
            new_params[name] = heuristics.get(name, lambda p, a: a[name])(dataset, new_params)

        return func(algorithm, post_method, dataset, param_names, self.metric, *[new_params[n] for n in param_names])

    def save_to_file(self, path: Path):
        with path.open("w") as f:
            json.dump(self.results, f)

    def finalize(self):
        for algorithm in self.algorithms:
            print(f"Dropping docker containers {algorithm[0].image_name}")
            finalize_fn = algorithm[0].get_finalize_fn()
            finalize_fn()
