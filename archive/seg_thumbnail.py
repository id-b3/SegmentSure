#!/usr/bin/env python3

import argparse
import re
import multiprocessing as mp
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import nibabel as nib
from tqdm import tqdm

plt.rcParams.update({
    "savefig.facecolor": "black",
    "savefig.edgecolor": "black"
})


def crop_image(image: np.ndarray, padding: tuple = (0, 0, 0)) -> np.ndarray:
    """
    Crop a 3D mask to minimum size + padding
    :param image: 3D mask
    :param padding: voxels to pad in the x, y, z axes
    :return: cropped 3D mask
    """

    def fit_to_image(boundbox: tuple):
        # get the max between x1 and 0 (lower bound)
        # and min between x2 and max image size (upper bound)
        fx1 = (max(boundbox[0][0], 0), min(boundbox[0][1], image.shape[0]))
        fy1 = (max(boundbox[1][0], 0), min(boundbox[1][1], image.shape[1]))
        fz1 = (max(boundbox[2][0], 0), min(boundbox[2][1], image.shape[2]))
        return fx1, fy1, fz1

    # Find the coordinates of the largest rectangle with the mask.
    idx_mask = np.argwhere(
        image != 0
    )  # Get the coordinates of the non-zero elements (tilde is an inverse of the mask)
    x1 = (
        min(idx_mask[:, 0]) - padding[0]
    )  # Get the minimum x coordinate of the non-zero elements and pad it with the borders
    x2 = (
        max(idx_mask[:, 0]) + padding[0]
    )  # Get the maximum x coordinate of the non-zero elements and pad it with the borders
    y1 = min(idx_mask[:, 1]) - padding[1]
    y2 = max(idx_mask[:, 1]) + padding[1]
    z1 = min(idx_mask[:, 2]) - padding[2]
    z2 = max(idx_mask[:, 2]) + padding[2]

    coords = fit_to_image(
        ((x1, x2), (y1, y2),
         (z1, z2)))  # Make sure the bounding box is within the image.
    cropped_img = image[coords[0][0]:coords[0][1], coords[1][0]:coords[1][1],
                        coords[2][0]:coords[2][1], ]  # Crop the image.
    return cropped_img


def process_segmentation(in_seg):

    air_seg = nib.load(in_seg).get_fdata()
    air_seg = crop_image(air_seg, padding=(4, 4, 4))
    f, axarr = plt.subplots(1, 3, figsize=(42, 12))
    axarr[0].imshow(np.rot90(air_seg.sum(axis=0)),
                    interpolation="hanning",
                    cmap="gray")
    axarr[1].imshow(np.rot90(air_seg.sum(axis=1)),
                    interpolation="hanning",
                    cmap="gray")
    axarr[2].imshow(air_seg.sum(axis=2), interpolation="hanning", cmap="gray")
    axarr[0].axis("off")
    axarr[1].axis("off")
    axarr[2].axis("off")
    plt.tight_layout()
    id_name = re.search(r'\d{6}', str(in_seg)).group()
    f.savefig(f"{in_seg.parent.parent}/Segmentation_Thumb/{id_name}.jpg")
    plt.close()


def main(args):
    list_segs = [f for f in Path(args.in_seg).iterdir() if f.is_file()]
    list_segs.sort()
    p = mp.Pool(16)
    list(tqdm(p.imap(process_segmentation, list_segs), total=len(list_segs)))
    p.close()
    p.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("in_seg", type=str, help="Input segmentation file.")
    in_args = parser.parse_args()
    main(in_args)
