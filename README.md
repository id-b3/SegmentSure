<!-- This is a README for a segmentation review tool on GitHub. -->

# Segmentation Review Tool

This tool is designed to help with the review of segmentation models. It takes in an input image and displays the results of the segmentation model's predictions. The tool also allows for manual adjustments to the predicted segmentation masks.


# Overview of directory
    src
      __pycache__
      __init__.py
      dataloader.py
      filedialog.py
      likert.py
      segviewer.py
    utils
    .gitignore
    LICENSE
  ▶ README.md
    SegSure.py
    requirements.txt
## Getting Started

### Prerequisites

This tool requires Python 3 and the following packages:

- OpenCV
- Numpy
- Matplotlib

### Installation

Clone this repository:


Install the required packages:


## Usage

To use the tool, run the following command:


Replace `input_image.jpg` with your own image and `model.h5` with the path to your segmentation model.

## Manual Adjustments

To make manual adjustments to the predicted segmentation masks, use the mouse to draw on the displayed image. The tool will save the adjusted masks in a separate file.

## Acknowledgments

This tool was inspired by the work of [Author Name](https://authorwebsite.com/).

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
