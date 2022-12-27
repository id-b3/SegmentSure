from pathlib import Path
import pandas as pd
from tqdm import tqdm


in_path = Path("/media/dudzie/T7Touch/Data/ImaLife_BronchialParameters/")
path_list = [f for f in in_path.iterdir() if f.is_dir()]
series_list = []

for dir in tqdm(path_list):
    try:
        bp_file = next(dir.glob("bp_summary_redcap.csv"))
        pd_series = pd.read_csv(str(bp_file))
        series_list.append(pd_series)
    except StopIteration:
        print(f"no summary for {dir.stem}")

breakpoint()
