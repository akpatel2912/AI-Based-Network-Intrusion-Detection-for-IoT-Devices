
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]          # .../ml
INPUT_PATH = BASE / "data" / "raw" / "df_Binary_FL_CICIoT2023.csv"
OUTPUT_PATH = BASE / "data" / "processed" / "processed_data.csv"


def main():
    df = pd.read_csv(INPUT_PATH)
    print("Original shape:", df.shape)

    if "Unnamed: 0" in df.columns:          # leftover index column
        df = df.drop(columns=["Unnamed: 0"])

    df = df.replace([np.inf, -np.inf], np.nan)
    print("Missing values per column:\n", df.isnull().sum())
    df = df.dropna()

    print("Duplicate rows:", df.duplicated().sum())
    df = df.drop_duplicates()

    print("Final shape:", df.shape)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print("Saved:", OUTPUT_PATH)


if __name__ == "__main__":
    main()
