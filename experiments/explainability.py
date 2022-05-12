import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import fire
from pathlib import Path


def main(dataset_path: Path, explainability_path: Path):
    df = pd.read_csv(dataset_path)
    exp = np.genfromtxt(explainability_path, delimiter=",")

    for c in range(df.shape[1] - 2):
        #plt.plot(df.iloc[:, c+1], label=f"channel {c}")
        pass

    plt.plot(df.iloc[:, -1], label="anomaly")

    for c in range(exp.shape[1]):
        plt.plot(exp[:, c], label=f"contribution {c}")

    plt.legend()
    plt.show()


if __name__ == "__main__":
    fire.Fire(main)
