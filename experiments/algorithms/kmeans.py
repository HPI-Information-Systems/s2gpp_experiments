from timeeval.adapters import DockerAdapter
from timeeval_experiments.algorithms.kmeans import post_kmeans
from .utils import get_docker_adapter


def kmeans() -> DockerAdapter:
    return get_docker_adapter("registry.gitlab.hpi.de/akita/i/kmeans")
