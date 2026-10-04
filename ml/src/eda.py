
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA_PATH = BASE / "data" / "processed" / "processed_data.csv"
OUT = BASE / "data" / "processed" / "eda"
TARGET = "sub_label"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PATH)
    features = [c for c in df.columns if c != TARGET]

    print("Shape:", df.shape)
    print("\nTarget balance:\n", df[TARGET].value_counts())
    print("\nStatistics:\n", df.describe().T.round(3))
    print("\nMean per class:\n", df.groupby(TARGET)[features].mean().T.round(3))
    corr = df.corr()
    print("\nCorrelation with target:\n", corr[TARGET].drop(TARGET).round(3).sort_values())

    # outliers by the 1.5 * IQR rule
    q1, q3 = df[features].quantile(0.25), df[features].quantile(0.75)
    iqr = q3 - q1
    out = ((df[features] < q1 - 1.5 * iqr) | (df[features] > q3 + 1.5 * iqr)).mean() * 100
    print("\nOutlier % per feature (IQR rule):\n", out.round(2))

    df[TARGET].map({0: "Normal", 1: "Attack"}).value_counts().plot.bar(color=["#34d399", "#f87171"])
    plt.title("Class balance"); plt.tight_layout(); plt.savefig(OUT / "class_balance.png"); plt.close()

    fig, axes = plt.subplots(2, 4, figsize=(16, 7))
    for ax, f in zip(axes.ravel(), features):
        for label, color in [(0, "#34d399"), (1, "#f87171")]:
            ax.hist(df.loc[df[TARGET] == label, f], bins=40, alpha=0.6, color=color)
        ax.set_title(f)
    plt.tight_layout(); plt.savefig(OUT / "distributions.png"); plt.close()

    plt.figure(figsize=(8, 6)); plt.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1); plt.colorbar()
    plt.xticks(range(len(corr)), corr.columns, rotation=45, ha="right"); plt.yticks(range(len(corr)), corr.columns)
    plt.title("Correlation matrix"); plt.tight_layout(); plt.savefig(OUT / "correlation.png"); plt.close()
    print("\nPlots saved to", OUT)


if __name__ == "__main__":
    main()
