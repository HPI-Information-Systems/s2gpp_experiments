import argparse
import sys
from pathlib import Path
from typing import List, Optional
from timeeval import DatasetManager, TrainingType

from hyperopt.algorithms import define_algorithms
from hyperopt import Hyperopt


def define_datasets(filters: List[Path], training_type: Optional[TrainingType] = None) -> List[Path]:
    dm = DatasetManager("data/GutenTAG")
    datasets = [dm.get_dataset_path(dataset_id) for dataset_id in dm.select(training_type=training_type)]

    if len(filters) > 0:
        datasets = list(filter(lambda d: d.parent.name in filters, datasets))

    return datasets


def main(args: argparse.Namespace):
    algorithms = define_algorithms(args.algorithms)
    datasets = define_datasets(args.datasets, args.training_type)

    opt = Hyperopt(algorithms, datasets, n_calls=args.hyperopt_calls)
    opt.optimize()
    opt.save_to_file(args.output_file)


def prepare_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--algorithms", nargs="+", default=[], help="What algorithms to use (default: all)")
    parser.add_argument("--datasets", nargs="+", default=[], help="What datasets to use (default: all)")
    parser.add_argument("--hyperopt-calls", type=int, default=10, help="How often to call one algorithm on one dataset (>= 10)")
    parser.add_argument("--dataset-dir", type=Path, default=Path("data/GutenTAG"), help="Directory holding datasets.csv")
    parser.add_argument("--output-file", type=Path, default=Path("./results.json"), help="Path for json output")
    parser.add_argument("--training-type", type=TrainingType, required=False)

    return parser.parse_args(sys.argv[1:])


if __name__ == '__main__':
    main(prepare_args())
