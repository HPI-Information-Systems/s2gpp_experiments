from typing import Dict, Any, Optional

import numpy as np
from durations import Duration
from timeeval import Algorithm, TrainingType, InputDimensionality
from timeeval.adapters import DockerAdapter
from timeeval.params import ParameterConfig
from timeeval.utils.window import ReverseWindowing


def post_mstamp(scores: np.ndarray, args: dict) -> np.ndarray:
    window_size = args.get("hyper_params", {}).get("anomaly_window_size", 50)
    return ReverseWindowing(window_size=window_size).fit_transform(scores)


_mstamp_parameters: Dict[str, Dict[str, Any]] = {
    "anomaly_window_size": {
        "defaultValue": 30,
        "description": "Size of the sliding window.",
        "name": "anomaly_window_size",
        "type": "Int"
    },
    "random_state": {
        "defaultValue": 42,
        "description": "Seed for random number generation.",
        "name": "random_state",
        "type": "Int"
    }
}


def mstamp(params: ParameterConfig = None, skip_pull: bool = False, timeout: Optional[Duration] = None) -> Algorithm:
    return Algorithm(
        name="mSTAMP",
        main=DockerAdapter(
            image_name="mut:5000/akita/mstamp",
            tag="799da4dc",
            skip_pull=skip_pull,
            timeout=timeout,
            group_privileges="akita",
        ),
        preprocess=None,
        postprocess=post_mstamp,
        param_schema=_mstamp_parameters,
        param_config=params or ParameterConfig.defaults(),
        data_as_file=True,
        training_type=TrainingType.UNSUPERVISED,
        input_dimensionality=InputDimensionality("multivariate")
    )
