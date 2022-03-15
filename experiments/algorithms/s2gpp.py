from typing import List, Optional, Dict, Any

import numpy as np
from durations import Duration
from timeeval import Algorithm, TrainingType, InputDimensionality
from timeeval.adapters import DockerAdapter
from timeeval.params import ParameterConfig
from timeeval.utils.window import ReverseWindowing
from .utils import get_docker_adapter


def get_hyperopt_params() -> List:
    # return [2.7395792737617386, 0.08869210174190788, 1.5, 100] best median
    return [1.3210416017417068, 0.7696339417210919, 1.5, 100]

def post_s2gpp(scores: np.ndarray, args: dict) -> np.ndarray:
    pattern_length = args.get("hyper_params", {}).get("pattern-length", 50)
    query_length = args.get("hyper_params", {}).get("query-length", 75)
    size = pattern_length + query_length
    return ReverseWindowing(window_size=size).fit_transform(scores)


def s2gpp() -> DockerAdapter:
    return get_docker_adapter("mut:5000/akita/s2gpp", "0.3.2")


_s2gpp_parameters: Dict[str, Dict[str, Any]] = {
    "pattern-length": {
        "name": "pattern-length",
        "type": "Int",
        "defaultValue": 50,
        "description": "Size of the sliding window, independent of anomaly length, but should in the best case be larger."
    },
    "latent": {
        "name": "latent",
        "type": "Int",
        "defaultValue": 16,
        "description": "Size of latent embedding space. This space is the input for the PCA calculation afterwards."
    },
    "rate": {
        "name": "rate",
        "type": "Int",
        "defaultValue": 100,
        "description": "Number of angles used to extract pattern nodes. A higher value will lead to high precision, but at the cost of increased computation time."
    },
    "threads": {
        "name": "threads",
        "type": "Int",
        "defaultValue": 1,
        "description": "Number of helper threads started besides the main thread. (min=1)"
    },
    "query-length": {
        "name": "query-length",
        "type": "Int",
        "defaultValue": 75,
        "description": "Size of the sliding windows used to find anomalies (query subsequences). query-length must be >= pattern-length!"
    }
}


def s2gpp_timeeval(name: str, params: ParameterConfig = None, skip_pull: bool = False, timeout: Optional[Duration] = None) -> Algorithm:
    return Algorithm(
        name=name,
        main=DockerAdapter(
            image_name="sopedu:5000/akita/s2gpp",
            tag="0.3.2",
            skip_pull=skip_pull,
            timeout=timeout,
            group_privileges="akita",
        ),
        preprocess=None,
        postprocess=post_s2gpp,
        param_schema=_s2gpp_parameters,
        param_config=params or ParameterConfig.defaults(),
        data_as_file=True,
        training_type=TrainingType.UNSUPERVISED,
        input_dimensionality=InputDimensionality("multivariate")
    )
