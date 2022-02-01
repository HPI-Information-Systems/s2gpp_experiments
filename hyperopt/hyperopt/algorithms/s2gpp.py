import numpy as np
from timeeval.adapters import DockerAdapter
from timeeval.utils.window import ReverseWindowing
from .utils import get_docker_adapter


def post_s2gpp(scores: np.ndarray, args: dict) -> np.ndarray:
    pattern_length = args.get("hyper_params", {}).get("pattern-length", 50)
    query_length = args.get("hyper_params", {}).get("query-length", 75)
    size = pattern_length + query_length
    return ReverseWindowing(window_size=size).fit_transform(scores)


def s2gpp() -> DockerAdapter:
    return get_docker_adapter("mut:5000/akita/s2gpp", "0.3.2")