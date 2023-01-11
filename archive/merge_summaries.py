from pathlib import Path
import pandas as pd
from tqdm import tqdm


in_path = Path("./summary_csvs/")
path_list = [f for f in in_path.iterdir() if f.is_file()]
series_list = []

for file in tqdm(path_list):
    try:
        pd_series = pd.read_csv(str(file))
        series_list.append(pd_series)
    except StopIteration:
        print(f"no summary for {dir.stem}")

df_merge = pd.concat(series_list)
df_merge.to_csv("merged_summaries.csv", index=False)
