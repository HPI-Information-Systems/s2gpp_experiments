from pathlib import Path
from typing import Dict, Any, Type

from . import BaseHeuristic


class SiblingHeuristic(BaseHeuristic):
    def __init__(self, dataset_dir: Path, sibling: str, param: str, dtype: Type):
        super().__init__(dataset_dir)
        self.sibling = sibling
        self.param = param
        self.dtype = dtype

    def _call(self, _dataset: Path, params: Dict[str, Any]) -> Any:
        sib = params[self.sibling]
        factor = params[self.param]
        return self.dtype(sib * factor)
