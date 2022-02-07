from pathlib import Path
from typing import Any, Callable, Dict
import abc

import pandas as pd

Heuristic = Callable[[Path, Dict[str, Any]], Any]


class BaseHeuristic(abc.ABC):
    def __init__(self, dataset_dir: Path):
        self.datasets = pd.read_csv(dataset_dir / "datasets.csv")

    def _get_attr(self, attr: str, dataset: Path) -> Any:
        return self.datasets[self.datasets.test_path == "/".join(str(dataset).split("/")[-2:])].iloc[0][attr]

    @abc.abstractmethod
    def _call(self, dataset: Path, params: Dict[str, Any]) -> Any:
        ...

    def __call__(self, dataset: Path, params: Dict[str, Any]) -> Any:
        return self._call(dataset, params)
