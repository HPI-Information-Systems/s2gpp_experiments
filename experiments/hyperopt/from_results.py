import json
from io import StringIO
from pathlib import Path
import re

import numpy as np
from tqdm import trange
import time, os

from ..algorithms import Method
from .base import BaseHyperopt
from .utils import get_stdout


class FromResults(BaseHyperopt):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open("results.only.patternlength.json", "r") as f:
            self.loaded_results = json.load(f)

    def optimize(self):
        pb = trange(len(self.algorithms) * len(self.datasets))
        pb.update(self._count_results())
        time.sleep(1)
        for algorithm in self.algorithms:
            for dataset in self.datasets:
                if self._combination_not_yet_done(algorithm, dataset):
                    try:
                        self.from_results(dataset, algorithm)
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        pb.write(f"Error occurred: {e} Continue with next optimization")
                        self._add_error_entry(algorithm, dataset)
                    pb.update(1)

    def from_results(self, dataset: Path, method: Method):
        algorithm, params, post_method, heuristics = method
        param_names, _ = zip(*params.items())
        params = self.loaded_results["mut:5000/akita/s2gpp"][str(dataset)]["location"]

        buf = StringIO()

        with get_stdout(buf):
            self._call_heuristics(algorithm, post_method, dataset, param_names, heuristics, *params)

        n_trans = re.findall(r"[#]Transitions\W[=]\W(\d+)", buf.getvalue())

        self.results[algorithm.image_name][str(dataset)]["transitions"] = n_trans
        self.results[algorithm.image_name][str(dataset)]["location"] = [int(x) if type(x) == np.int64 else x for x in params]

    def _add_error_entry(self, algorithm: Method, dataset: os.PathLike):
        self.results[algorithm[0].image_name][str(dataset)]["transitions"] = []
        self.results[algorithm[0].image_name][str(dataset)]["location"] = []
