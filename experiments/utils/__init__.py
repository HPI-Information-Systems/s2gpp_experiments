from contextlib import contextmanager, redirect_stderr, redirect_stdout
from os import devnull
from pathlib import Path
import random
from typing import List, Optional

from timeeval import TrainingType, InputDimensionality, DatasetManager


def define_datasets(filters: List[Path], dataset_dir: Path, training_type: Optional[TrainingType] = None, input_dimensionality: Optional[InputDimensionality] = None, sample_n: Optional[int] = None) -> List[Path]:
    dm = DatasetManager(dataset_dir)
    datasets = [dm.get_dataset_path(dataset_id) for dataset_id in dm.select(training_type=training_type, input_dimensionality=input_dimensionality)]

    if len(filters) > 0:
        datasets = list(filter(lambda d: d.parent.name in filters, datasets))

    if sample_n is not None:
        datasets = random.choices(datasets, k=sample_n)

    return datasets


@contextmanager
def suppress_stdout_stderr():
    """A context manager that redirects stdout and stderr to devnull"""
    with open(devnull, 'w') as fnull:
        with redirect_stderr(fnull) as err, redirect_stdout(fnull) as out:
            yield (err, out)
