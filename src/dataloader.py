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
        self.image_list = [
            str(i) for i in Path(image_dir).iterdir() if i.is_file()
        ]
        self.summary_df = pd.read_csv(summary_path)
        self.seg_list = [
            str(s) for s in Path(seg_dir).iterdir() if s.is_file()
        ]

        self.save_path = Path(summary_path)

        self.prep_df()
        self.get_flagged_df()

    def prep_df(self):
        self.summary_df["bp_reviewed"] = self.summary_df.get("bp_reviewed", 0)
        self.summary_df["bp_err_reason"] = self.summary_df.get(
            "bp_err_reason", "")
        self.summary_df["bp_leak_score"] = self.summary_df.get(
            "bp_leak_score", -1)
        self.summary_df["bp_segmental_score"] = self.summary_df.get(
            "bp_segmental_score", -1)
        self.summary_df["bp_subsegmental_score"] = self.summary_df.get(
            "bp_subsegmental_score", -1)
        self.summary_df["bp_inspect"] = self.summary_df.get("bp_inspect", 0)

    def get_flagged_df(self):
        """
        Filters the summary by the bp_seg_error flag.
        """
        self.flagged_df = self.summary_df.sort_values(by=["bp_reviewed", "bp_seg_error"],
                                                      ascending=[True, False])
        self.flagged_df.reset_index(drop=True, inplace=True)
        print(
            f"{len(self.flagged_df[(self.flagged_df.bp_seg_error == 1) & (self.flagged_df.bp_reviewed == 0)])} scans to review..."
        )
        print(f"Total scans: {len(self.flagged_df)}")
        print(f"Next scans: {self.flagged_df.bp_seg_error.head(20)}")

    def get_random_sample(self, number: int = 100):
        """
        Returns n random segmentations
        """
        self.random_df = self.summary_df.sample(number)
        self.random_df.reset_index(drop=True, inplace=True)

    def save_flagged_df(self):
        self.flagged_df.to_csv(str(self.save_path), index=False)
