from enum import Enum
from typing import Type

from .from_results import FromResults
from .no_opt import NoHyperopt
from .utils import func, suppress_stdout_stderr
from .base import BaseHyperopt
from .per_dataset import PerDatasetHyperopt
from .whole_collection import WholeCollectionHyperopt


class HyperoptMode(Enum):
    PER_DATASET = "per_dataset"
    WHOLE_COLLECTION = "whole_collection"
    NO_OPT = "no_opt"
    FROM_RESULTS = "from_results"

    def get_hyperopt(self) -> Type[BaseHyperopt]:
        if self == HyperoptMode.PER_DATASET:
            return PerDatasetHyperopt
        elif self == HyperoptMode.NO_OPT:
            return NoHyperopt
        elif self == HyperoptMode.FROM_RESULTS:
            return FromResults
        else:  # if self == HyperoptMode.WHOLE_COLLECTION
            return WholeCollectionHyperopt
