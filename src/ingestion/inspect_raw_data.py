from pathlib import Path

import pandas as pd


FREQUENCY_FILE = Path("data/raw/freMTPL2freq.pq")


frequency_df = pd.read_parquet(
    FREQUENCY_FILE,
    engine="fastparquet",
)


print("Dosya:", FREQUENCY_FILE)
print("Boyut:", frequency_df.shape)
print("Sütunlar:", frequency_df.columns.tolist())

print("\nİlk 5 satır:")
print(frequency_df.head())