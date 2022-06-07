import argparse
from pathlib import Path
from typing import Iterator, Tuple
import pandas as pd
import numpy as np
import docker
from docker.models.containers import Container
from durations import Duration
from timeeval import ResourceConstraints
from timeeval.adapters.docker import DockerAdapter, AlgorithmInterface
from timeeval.data_types import ExecutionType
from timeeval.utils.window import ReverseWindowing

GB = 1024 ** 3


class S2GPPExplainability(DockerAdapter):
    DATASET_TARGET_PATH = Path("/data")
    RESULTS_TARGET_PATH = Path("/results")
    SCORES_FILE_NAME = Path("docker-algorithm-scores.csv")
    EXPLAINABILITY_FILE_NAME = Path("docker-explainability-scores.csv")
    MODEL_FILE_NAME = Path("model.pkl")

    def __init__(self, tag: str = "latest", group_privileges="akita", *args, **kwargs):
        super().__init__("sopedu:5000/akita/s2gpp", tag, group_privileges, *args, **kwargs)

    def explain(self, dataset_path: Path, **hyper_params) -> np.ndarray:
        container = self._run_explainability(dataset_path, **hyper_params)
        self._run_until_timeout(container, {"resource_constraints": ResourceConstraints(train_timeout=Duration("10 minutes"))})
        directory = self._results_path({}, absolute=True)
        filename = self.EXPLAINABILITY_FILE_NAME
        exp_score = np.genfromtxt(directory / filename, delimiter=",")
        return self._post_process(exp_score, hyper_params.get("pattern-length", 50) + hyper_params.get("query-length", 75))

    def _post_process(self, data: np.ndarray, window_size: int) -> np.ndarray:
        dims = []
        for d in range(data.shape[1]):
            dims.append(
                ReverseWindowing(window_size=window_size).fit_transform(data[:, d])
            )
        return np.column_stack(dims)

    def _run_explainability(self, dataset_path: Path, **hyper_params) -> Container:
        client = docker.from_env()

        algorithm_interface = AlgorithmInterface(
            dataInput=(self.DATASET_TARGET_PATH / dataset_path.name).absolute(),
            dataOutput=(self.RESULTS_TARGET_PATH / self.SCORES_FILE_NAME).absolute(),
            modelInput=(self.RESULTS_TARGET_PATH / self.MODEL_FILE_NAME).absolute(),
            modelOutput=(self.RESULTS_TARGET_PATH / self.MODEL_FILE_NAME).absolute(),
            executionType=ExecutionType.EXECUTE.value,
            customParameters=hyper_params,
        )

        uid = DockerAdapter._get_uid()
        gid = DockerAdapter._get_gid(self.group)
        if not gid:
            gid = uid
        print(
            f"Running container '{self.image_name}:{self.tag}' with uid={uid} and gid={gid} privileges in {algorithm_interface.executionType} mode.")

        memory_limit, cpu_limit = self._get_compute_limits({})
        cpu_shares = int(cpu_limit * 1e9)
        print(f"Restricting container to {cpu_limit} CPUs and {memory_limit / GB:.3f} GB RAM")

        return client.containers.run(
            f"{self.image_name}:{self.tag}",
            f"execute-algorithm '{algorithm_interface.to_json_string()}'",
            volumes={
                str(dataset_path.parent.absolute()): {'bind': str(self.DATASET_TARGET_PATH), 'mode': 'ro'},
                str(self._results_path({}, absolute=True)): {'bind': str(self.RESULTS_TARGET_PATH), 'mode': 'rw'}
            },
            environment={
                "LOCAL_GID": gid,
                "LOCAL_UID": uid
            },
            mem_swappiness=0,
            mem_limit=memory_limit,
            memswap_limit=memory_limit,
            nano_cpus=cpu_shares,
            detach=True,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Explainability Experiment')
    parser.add_argument('--datasets', type=Path, help='Path to dataset directory')
    return parser.parse_args()


def loop_datasets(path: Path) -> Iterator[pd.Series]:
    df = pd.read_csv(path / 'datasets.csv')
    for _, dataset in df.iterrows():
        if dataset.train_type == "unsupervised":
            yield dataset


def get_anomalous_dim_num(dataset: pd.Series) -> int:
    """
    haystack-ecg-3-pattern-{dim}
    :param dataset:
    :return: index of anomalous channel
    """
    return int(dataset.dataset_name.split(".")[0].split("-")[4])


def get_anomalous_range(path: Path, dataset: pd.Series) -> Tuple[int, int]:
    labels = pd.read_csv(path / dataset.test_path).iloc[:, -1].values
    anomalous_idx = np.where(labels)[0]
    return anomalous_idx[0], anomalous_idx[-1]


def evaluate_contribution_score(score: np.ndarray, anomaly_range: Tuple[int, int], dim: int) -> bool:
    anomalous_score = score[anomaly_range[0]:anomaly_range[1]]
    return anomalous_score.max(axis=0).argmax() == dim


def get_contribution_score(args: argparse.Namespace, dataset: pd.Series) -> np.ndarray:
    algorithm = S2GPPExplainability("0.8.0", "phillip")
    hyper_params = {
        "pattern-length": int(dataset.max_anomaly_length),
        "latent": int(dataset.max_anomaly_length / 3),
        "query-length": int(dataset.max_anomaly_length * 1.0),
        "rate": 100,
        "clustering": "kde",
        "explainability": "",
        "anomaly-contribution-output-path": S2GPPExplainability.RESULTS_TARGET_PATH / S2GPPExplainability.EXPLAINABILITY_FILE_NAME
    }

    return algorithm.explain(args.datasets / dataset.test_path, **hyper_params)


def main(args: argparse.Namespace):
    results = []
    for dataset in loop_datasets(args.datasets):
        score = get_contribution_score(args, dataset)

        anomaly_dim = get_anomalous_dim_num(dataset)
        anomaly_range = get_anomalous_range(args.datasets, dataset)
        results.append({
            "dataset": dataset.dataset_name,
            "correct": evaluate_contribution_score(score, anomaly_range, anomaly_dim)
        })

    pd.DataFrame(results).to_csv("explainability-results.csv", index=False)


if __name__ == "__main__":
    args = parse_args()
    main(args)
