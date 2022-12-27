import pandas as pd

df = pd.read_csv("redcap_summary_corrected.csv")
df_error = df.loc[(df.bp_seg_error == 1)]
breakpoint()
