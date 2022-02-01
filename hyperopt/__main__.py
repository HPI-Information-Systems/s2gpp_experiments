import argparse
import sys
from pathlib import Path
from typing import List
from timeeval import DatasetManager

from hyperopt.algorithms import define_algorithms
from hyperopt import Hyperopt


def define_datasets() -> List[Path]:
    dm = DatasetManager("../data/GutenTAG")
    return [dm.get_dataset_path(dataset_id) for dataset_id in dm.select(dataset="sinus-combined-diff-1.unsupervised")]


def main(args: argparse.Namespace):
    print(args)
    return


    algorithms = define_algorithms()
    datasets = define_datasets()

    opt = Hyperopt(algorithms, datasets)
    opt.optimize()
    opt.save_to_file(args.output_file)


def prepare_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--algorithms", nargs="+", default=[], help="What algorithms to use (default: all)")
    parser.add_argument("--datasets", nargs="+", default=[], help="What datasets to use (default: all)")
    parser.add_argument("--hyperopt-calls", type=int, default=10, help="How often to call one algorithm on one dataset")
    parser.add_argument("--output-file", type=Path, default=Path("./results.json"), help="Path for json output")

    return parser.parse_args(sys.argv[1:])


if __name__ == '__main__':
    main(prepare_args())
