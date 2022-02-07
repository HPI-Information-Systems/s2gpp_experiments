import argparse
from pathlib import Path
from timeeval import TrainingType, Metric, InputDimensionality

from ..algorithms import define_algorithms
from . import HyperoptMode
from ..utils import define_datasets


def main(args: argparse.Namespace):
    algorithms = define_algorithms(args.algorithms, args.dataset_dir)
    datasets = define_datasets(args.datasets, args.dataset_dir, args.training_type, args.input_dimensionality, args.sample_n)

    opt_class = args.mode.get_hyperopt()
    opt = opt_class(algorithms, datasets, n_calls=args.hyperopt_calls, metric=args.metric, results_path=args.output_file if args.continues else None)
    try:
        opt.optimize()
    except KeyboardInterrupt:
        print("Interrupted! Saving already calculated results!")
    opt.save_to_file(args.output_file)
    opt.finalize()


def define_args(parser: argparse.ArgumentParser):
    parser.add_argument("--algorithms", nargs="+", default=[], help="What algorithms to use (default: all)")
    parser.add_argument("--datasets", nargs="+", default=[], help="What datasets to use (default: all)")
    parser.add_argument("--hyperopt-calls", type=int, default=10,
                        help="How often to call one algorithm on one dataset (>= 10)")
    parser.add_argument("--dataset-dir", type=Path, default=Path("data/GutenTAG"),
                        help="Directory holding datasets.csv")
    parser.add_argument("--output-file", type=Path, default=Path("./results.json"), help="Path for json output")
    parser.add_argument("--metric", type=lambda m: Metric(int(m)), default=Metric.ROC_AUC)
    parser.add_argument("--training-type", type=TrainingType, required=False)
    parser.add_argument("--input-dimensionality", type=InputDimensionality, required=False)
    parser.add_argument("--sample-n", type=int, required=False)
    parser.add_argument("--mode", type=HyperoptMode, default=HyperoptMode.PER_DATASET)
    parser.add_argument('--continue', dest='continues', action='store_true')
    parser.set_defaults(continues=False)
