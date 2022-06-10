import numpy as np
from timeeval.adapters import DockerAdapter
from .utils import get_docker_adapter


def post_dbstream(scores: np.ndarray, _args: dict) -> np.ndarray:
    return scores


def dbstream() -> DockerAdapter:
    return get_docker_adapter("registry.gitlab.hpi.de/akita/i/dbstream")
