import abc
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Dict, Optional

import tqdm
from timeeval.adapters import DockerAdapter

from .timer import Timer
from ..algorithms import Method
from ..utils import suppress_stdout_stderr


class BaseExperiment(abc.ABC):
    def __init__(self, method: Method, datasets: List[Path], params: Dict):
        self.datasets = datasets
        self.docker_adapter: DockerAdapter = method[0]
        self.params = params
        self.results = defaultdict(dict)

    def run(self):
        pb = tqdm.tqdm(self.datasets, desc=f"Datasets for {self.docker_adapter.image_name}", position=1)
        for dataset in pb:
            e = None
            with TemporaryDirectory(dir=".") as tmpdirname:
                with Timer() as timer:
                    result_file = Path(tmpdirname)
                    try:
                        with suppress_stdout_stderr():
                            self._run_command(dataset, result_file)
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        e = str(e)
                        pb.write(f"Error occurred: {e}! Continue with next optimization")
            self._finalize()
            self._record_result(timer, dataset, e)

    @abc.abstractmethod
    def _run_command(self, dataset: Path, result: Path):
        ...

    def _record_result(self, timer: Timer, dataset: Path, error: Optional[str]):
        self.results[dataset.parent.name]["duration"] = timer.duration
        if error is not None:
            self.results[dataset.parent.name]["error"] = error

    def _finalize(self):
        self.docker_adapter.get_finalize_fn()()
