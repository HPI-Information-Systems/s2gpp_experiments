from pathlib import Path
from typing import Dict, Any, Type

from . import BaseHeuristic


class DatasetAttrHeuristic(BaseHeuristic):
    def __init__(self, dataset_dir: Path, attr: str, param: str, dtype: Type):
        super().__init__(dataset_dir)
        self.attr = attr
        self.param = param
        self.dtype = dtype

    def _get_attr(self, dataset: Path) -> Any:
        return super()._get_attr(self.attr, dataset)

    def _call(self, dataset: Path, params: Dict[str, Any]) -> Any:
        attr = self._get_attr(dataset)
        return self.dtype(attr * params[self.param])
