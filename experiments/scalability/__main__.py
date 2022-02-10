import argparse
import json
from pathlib import Path
from typing import Dict
import tqdm

from .distributed_experiment import DistExperiment
from .non_distributed_experiment import NonDistExperiment
from ..algorithms import define_algorithms, Method
from ..utils import define_datasets


def get_params(algorithm: Method) -> Dict:
    search_space = algorithm[1]
    return {k: v[0] for k, v in search_space.items()}


def save_results(results: Dict, path: Path):
    with path.open("w") as f:
        json.dump(results, f)


def main(args: argparse.Namespace):
    algorithms = define_algorithms(args.algorithms, args.dataset_dir)
    datasets = define_datasets(args.datasets, args.dataset_dir)

    results: Dict[str, Dict] = {}
    exp_class = DistExperiment if args.distributed else NonDistExperiment

    for algorithm in tqdm.tqdm(algorithms, desc="Algorithms", position=0):
        exp = exp_class(algorithm, datasets, get_params(algorithm))
        try:
            exp.run()
        except KeyboardInterrupt:
            print("Interrupted! Saving already calculated results!")
            results[algorithm[0].image_name] = exp.results
            save_results(results, args.output_file)
            break
        results[algorithm[0].image_name] = exp.results
        save_results(results, args.output_file)


def sub(args: argparse.Namespace):
    algorithms = define_algorithms(args.algorithms, args.dataset_dir)
    datasets = define_datasets(args.datasets, args.dataset_dir)

    results: Dict[str, Dict] = {}
    exp_class = DistExperiment if args.distributed else NonDistExperiment

    for algorithm in tqdm.tqdm(algorithms, desc="Algorithms", position=0):
        exp = exp_class(algorithm, datasets, get_params(algorithm))
        try:
            exp.run()
        except KeyboardInterrupt:
            print("Interrupted! Saving already calculated results!")
            results[algorithm[0].image_name] = exp.results
            save_results(results, args.output_file)
            break
        results[algorithm[0].image_name] = exp.results
        save_results(results, args.output_file)


def define_args(parser: argparse.ArgumentParser):
    parser.add_argument("--algorithms", nargs="+", default=[], help="What algorithms to use (default: all)")
    parser.add_argument("--datasets", nargs="+", default=[], help="What datasets to use (default: all)")
    parser.add_argument("--dataset-dir", type=Path, default=Path("data/GutenTAG"), help="Directory holding datasets.csv")
    parser.add_argument("--output-file", type=Path, default=Path("./results.json"), help="Path for json output")
    parser.add_argument('--distributed', dest='distributed', action='store_true')
    parser.set_defaults(distributed=False)
