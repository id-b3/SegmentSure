from pathlib import Path
import re
import pandas as pd
from tqdm import tqdm


in_path = Path("/media/ivan/ID_B3Care/Data/Lung_Metrics/")
path_list = [f for f in in_path.iterdir() if f.is_file()]
path_list.sort()
series_list = []

for file in tqdm(path_list):
    try:
        pid = re.search(r'\d{6}', str(file)).group()
        df = pd.read_csv(str(file), index_col=0)
        pd_series = df.iloc[:, 1:3:2]
        pd_series = pd_series.rename(columns={"Perc Emphysema": pid})
        pd_series = pd_series.transpose()
        series_list.append(pd_series)
    except StopIteration:
        print(f"no summary for {dir.stem}")

df_merge = pd.concat(series_list)

df_merge.to_csv("merged_emphysema.csv")
