from pathlib import Path

from pydantic import ValidationError

from .base_experiment import BaseExperiment
from ..utils.dist_docker_adapter import DistDockerAdapter


class DistExperiment(BaseExperiment):
    def _run_command(self, dataset: Path, result: Path):
        self._valid_dist_docker_adapter()
        args = {
            "results_path": result,
            "hyper_params": self.params
        }
        self.docker_adapter(dataset, args)

    def _valid_dist_docker_adapter(self):
        docker_adapter_type = type(self.docker_adapter)
        if docker_adapter_type != DistDockerAdapter:
            raise ValidationError(f"The DistExperiment can only run with DistDockerAdapters! "
                                  f"You used {docker_adapter_type}.")
