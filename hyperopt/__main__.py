import argparse
import sys
import random
from pathlib import Path
from typing import List, Optional
from timeeval import DatasetManager, TrainingType, Metric, InputDimensionality

from hyperopt.algorithms import define_algorithms
from hyperopt import Hyperopt


def define_datasets(filters: List[Path], dataset_dir: Path, training_type: Optional[TrainingType] = None, input_dimensionality: Optional[InputDimensionality] = None, sample_n: Optional[int] = None) -> List[Path]:
    dm = DatasetManager(dataset_dir)
    datasets = [dm.get_dataset_path(dataset_id) for dataset_id in dm.select(training_type=training_type, input_dimensionality=input_dimensionality)]

    if len(filters) > 0:
        datasets = list(filter(lambda d: d.parent.name in filters, datasets))

    if sample_n is not None:
        datasets = random.choices(datasets, k=sample_n)

    return datasets


def main(args: argparse.Namespace):
    algorithms = define_algorithms(args.algorithms, args.dataset_dir)
    datasets = define_datasets(args.datasets, args.dataset_dir, args.training_type, args.input_dimensionality, args.sample_n)

    opt = Hyperopt(algorithms, datasets, n_calls=args.hyperopt_calls, metric=args.metric, results_path=args.output_file if args.continues else None)
    try:
        opt.optimize()
    except KeyboardInterrupt:
        print("Interrupted! Saving already calculated results!")
    opt.save_to_file(args.output_file)


def prepare_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--algorithms", nargs="+", default=[], help="What algorithms to use (default: all)")
    parser.add_argument("--datasets", nargs="+", default=[], help="What datasets to use (default: all)")
    parser.add_argument("--hyperopt-calls", type=int, default=10, help="How often to call one algorithm on one dataset (>= 10)")
    parser.add_argument("--dataset-dir", type=Path, default=Path("data/GutenTAG"), help="Directory holding datasets.csv")
    parser.add_argument("--output-file", type=Path, default=Path("./results.json"), help="Path for json output")
    parser.add_argument("--metric", type=lambda m: Metric(int(m)), default=Metric.ROC_AUC)
    parser.add_argument("--training-type", type=TrainingType, required=False)
    parser.add_argument("--input-dimensionality", type=InputDimensionality, required=False)
    parser.add_argument("--sample-n", type=int, required=False)
    parser.add_argument('--continue', dest='continues', action='store_true')
    parser.set_defaults(continues=False)

    return parser.parse_args(sys.argv[1:])


if __name__ == '__main__':
    main(prepare_args())
