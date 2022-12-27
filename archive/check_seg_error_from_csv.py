import pandas as pd
import numpy as np

df = pd.read_csv("redcap_summary.csv")


def check_row(tlv, airvol, tcount):
    lungs = tlv > 8.0 or tlv < 3.0
    airs = airvol > 0.4 or airvol < 0.08
    counts = tcount > 400 or tcount < 150

    if lungs or airs or counts:
        return 1
    else:
        return 0


df['bp_seg_error'] = np.where((df.bp_tlv > 8.0) | (df.bp_airvol > 0.4) | (df.bp_tcount > 400) | (df.bp_tlv < 3.0) | (df.bp_airvol < 0.08) | (df.bp_tcount < 150), 1, 0)

df.to_csv("redcap_summary_corrected.csv")
