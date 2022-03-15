import argparse
from pathlib import Path

from .third_eye import ThirdEye
from ..algorithms import define_algorithms


def main(args: argparse.Namespace):
    algorithm = define_algorithms(["sopedu:5000/akita/s2gpp"], args.dataset.parent.parent)[0]
    third_eye = ThirdEye(algorithm, args.dataset, args.output_dir, args.anomaly_length).open_lid()
    third_eye.run()
    print(f"Score {third_eye.score()}")


def define_args(parser: argparse.ArgumentParser):
    parser.add_argument("--dataset", type=Path, help="Path to input dataset")
    parser.add_argument("--output-dir", type=Path, default=Path("."), help="Directory for score output")
    parser.add_argument("--anomaly-length", type=int, help="Expected anomaly length")
