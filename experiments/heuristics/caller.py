from pathlib import Path
from typing import Dict

from timeeval.adapters import DockerAdapter

from experiments.algorithms import Method, PostMethod, Heuristics
from experiments.utils import run_docker_algorithm


class HeuristicCaller:
    def __init__(self, method: Method, params: Dict, dataset: Path, result_file: Path):
        self.algorithm: DockerAdapter = method[0]
        self.params: Dict = params
        self.post_method: PostMethod = method[2]
        self.heuristics: Heuristics = method[3]
        self.dataset = dataset
        self.result_file = result_file

    def run(self) -> Dict:
        new_params = self.params
        for name, p in self.params.items():
            new_params[name] = self.heuristics.get(name, lambda p, a: a[name])(self.dataset, new_params)

        return run_docker_algorithm(self.algorithm, self.dataset, self.result_file, new_params)
