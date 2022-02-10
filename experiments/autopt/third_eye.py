from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, List, Dict

import numpy as np
import pandas as pd
from timeeval import Metric

from ..algorithms import Method
from ..heuristics.caller import HeuristicCaller
from ..hyperopt import PerDatasetHyperopt
from ..utils import calculate_metric


class ThirdEye:
    def __init__(self,
                 algorithm: Method,
                 dataset_path: Path,
                 output_dir: Path,
                 anomaly_length: int,
                 bo_steps: int = 20,
                 generation_factor: int = 5):
        self.algorithm = algorithm
        self.dataset_path = dataset_path
        self.output_path = output_dir
        self.anomaly_length = anomaly_length
        self.bo_steps = bo_steps
        self.generation_factor = generation_factor
        self.optimal_setting: Optional[Dict] = None
        self.run_args: Optional[Dict] = None

    def open_lid(self) -> ThirdEye:
        with TemporaryDirectory() as tmpdir:
            validation_dataset = self._generate_validation_dataset(Path(tmpdir))
            hyperopt = PerDatasetHyperopt(
                [self.algorithm],
                [validation_dataset],
                n_calls=self.bo_steps
            )

            hyperopt.optimize()
            hyperopt.finalize()

        results = hyperopt.results[self.algorithm[0].image_name][str(validation_dataset)]
        print(results)
        self.optimal_setting = results["location"]
        score = results["score"]
        print(f"Found optimal setting {self.optimal_setting} with score {score}")

        return self

    def run(self):
        caller = HeuristicCaller(self.algorithm, self.optimal_setting, self.dataset_path, self.output_path)
        self.run_args = caller.run()

    def score(self, metric=Metric.ROC_AUC):
        return calculate_metric(self.algorithm[2], self.run_args, self.dataset_path, metric)

    def _generate_validation_dataset(self, directory: Path) -> Path:
        ts_len = self.anomaly_length * self.generation_factor
        ts: pd.DataFrame = pd.read_csv(self.dataset_path).iloc[:ts_len]

        anomaly_start_idx = int(self.generation_factor / 2)
        anomaly_end_idx = anomaly_start_idx + self.anomaly_length
        ts.iloc[anomaly_start_idx:anomaly_end_idx, 1:-1] = np.random.random(self.anomaly_length)
        ts.iloc[anomaly_start_idx:anomaly_end_idx, -1] = 1

        path = directory / "thirdeye.csv"
        ts.to_csv(path, index=False)
        return path
