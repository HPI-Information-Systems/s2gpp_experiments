from timeeval.adapters import DockerAdapter
from timeeval_experiments.algorithms.torsk import _post_torsk
from .utils import get_docker_adapter


def torsk() -> DockerAdapter:
    return get_docker_adapter("sopedu:5000/akita/torsk")
