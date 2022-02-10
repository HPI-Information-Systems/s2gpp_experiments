import argparse
import sys

from experiments.hyperopt.__main__ import main as hyperopt, define_args as define_hyperopt_args
from experiments.scalability.__main__ import main as scalability, define_args as define_scalability_args
from experiments.autopt.__main__ import main as autopt, define_args as define_autopt_args


def prepare_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subparser")

    hyperopt_parser = subparsers.add_parser("hyperopt")
    define_hyperopt_args(hyperopt_parser)

    hyperopt_parser = subparsers.add_parser("scalability")
    define_scalability_args(hyperopt_parser)

    hyperopt_parser = subparsers.add_parser("autopt")
    define_autopt_args(hyperopt_parser)

    return parser.parse_args(sys.argv[1:])


if __name__ == '__main__':
    args = prepare_args()
    if args.subparser == "hyperopt":
        hyperopt(args)
    elif args.subparser == "scalability":
        scalability(args)
    elif args.subparser == "autopt":
        autopt(args)
