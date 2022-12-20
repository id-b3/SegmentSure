from pathlib import Path
import pandas as pd


class DataLoader():

    def __init__(self, image_dir: str, seg_dir: str, summary_path: str):
        """
        Loads the images, segmentations and summary dataframes.

        :param image_dir str: Path containing segmentation images.
        :param seg_dir str: Path containing nifti format segmentations.
        :param summary_path str: Summary csv path.
        """
        self.image_list = [i for i in Path(image_dir).iterdir() if i.is_dir()]
        self.summary_df = pd.read_csv(summary_path)
        self.seg_list = [s for s in Path(seg_dir).iterdir() if s.is_dir()]

        self.prep_df()
        self.get_flagged_df()

    def prep_df(self):
        self.summary_df["bp_reviewed"] = self.summary_df.get("bp_reviewed", 0)
        self.summary_df["bp_err_reason"] = self.summary_df.get(
            "bp_err_reason", "")

    def get_flagged_df(self):
        """
        Filters the summary by the bp_seg_error flag.

        """
        self.flagged_df = self.summary_df[self.summary_df.bp_seg_error == 1]
        self.flagged_df.reset_index(drop=True)
