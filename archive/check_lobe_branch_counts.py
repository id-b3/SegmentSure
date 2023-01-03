#!/usr/bin/env python3

from pathlib import Path
import argparse
import pandas as pd


def main(args):

    main_dir = Path(args.pickle_dir)
    list_pickles = [str(p) for p in main_dir.iterdir() if p.is_file()]

    def _check_lobes(row):
        pid = row["participant_id"]
        pickle_search = [p for p in list_pickles if str(pid) in p]
        pickle_path = pickle_search[0]
        df = pd.read_pickle(str(pickle_path))

        try:
            lobes = df.lobes[df.lobes.astype(bool)].value_counts()
            if (len(lobes) < 5) or (lobes < 5).any():
                print(f"Potentially discontinuous segmentation in {row['participant_id']}")
                row["bp_seg_error"] = 1
        except AttributeError as e:
            print(f"Error processing pickle for {pid}")

        return row

    sum_df = pd.read_csv(args.merged_csv)
    sum_df = sum_df.apply(_check_lobes, axis=1)
    sum_df.to_csv("merged_summaries_final.csv", index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("merged_csv", type=str, help="Path to the merged summary file.")
    parser.add_argument("pickle_dir", type=str, help="Path for pickles directory.")
    args = parser.parse_args()

    main(args)
