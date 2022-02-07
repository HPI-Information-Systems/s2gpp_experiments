from pathlib import Path
from .base_experiment import BaseExperiment


class NonDistExperiment(BaseExperiment):
    def _run_command(self, dataset: Path, result: Path):
        args = {
            "results_path": result,
            "hyper_params": self.params
        }
        self.docker_adapter(dataset, args)
