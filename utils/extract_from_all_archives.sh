#!/bin/bash

main_dir=$1
extract_pattern=$2
output_dir=$3
save_pattern=$4
tarball=${5:-"*_bronchial_results.tar.gz"}

if [ $# -ne 4 ]; then
    echo "Script to extract a file pattern from zips in subdirs."
    echo "Usage: $0 MAIN_DIRECTORY EXTRACTION_PATTERN OUTPUT_DIRECTORY SAVE_PATTERN"
    echo "Please provide all the necessary arguments as outlined above"
    exit 1
fi

echo "Main:    $main_dir"
echo "Pattern: $extract_pattern"
echo "Output:  $output_dir"
echo "Save:    [ID]_$save_pattern"

for subdir in "$main_dir"/*/ ; do
    echo $subdir
    # tar xvf $subdir/*_bronchial_results.tar.gz 
    filename=$(tar tf $subdir/$tarball --wildcards $extract_pattern)
    if [ -n "$filename" ]; then
        echo "Extracting $filename..."
        save_name="$(basename $subdir)_$save_pattern"
        transform_exp="s|$filename|$save_name|"
        echo $transform_exp
        tar --transform=$transform_exp -C "$output_dir" -xf "$subdir"/$tarball "$filename" &
    else
        echo "Pattern not found in $subdir"
    fi

done

