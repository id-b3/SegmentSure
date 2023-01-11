find /mnt/f/Data/Segmentation_Images/ -type f -name "*.nii.gz" -exec sh -c "echo {} | grep -o '[0-9]\{6\}' | xargs -P 4 -I {1} ./archive/seg_thumbnail.py {} /mnt/f/Data/Segmentation_Thumb/{1}.jpg" \;
