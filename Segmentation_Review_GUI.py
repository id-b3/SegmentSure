import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
                             QPushButton, QVBoxLayout, QWidget)

from mayavi import mlab
import numpy as np
from skimage import data, filters, measure


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the Mayavi widget and add it to the main window
        self.mayavi_widget = mlab.get_engine().get_qt_widget()
        self.setCentralWidget(self.mayavi_widget)

        # Create the buttons and labels
        prev_button = QPushButton("Prev")
        next_button = QPushButton("Next")
        tlv_label = QLabel("TLV")
        tav_label = QLabel("TAV")
        tac_label = QLabel("TAC")

        # Create the button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(prev_button)
        button_layout.addWidget(next_button)

        # Create the label layout
        label_layout = QHBoxLayout()
        label_layout.addWidget(tlv_label)
        label_layout.addWidget(tav_label)
        label_layout.addWidget(tac_label)

        # Create the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.mayavi_widget)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(label_layout)

        # Set the main layout for the main window
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Set the shortcut for switching to the image
        self.addAction(QKeySequence("T"), self.switch_to_image)

        # Generate the mesh using scikit-image
        self.mesh = measure.marching_cubes(data.checkerboard(), 0)
        self.mesh_actor = mlab.triangular_mesh(*self.mesh[:3], self.mesh[3])
        self.image_actor = None

    def switch_to_image(self):
        # Toggle between showing the mesh and the image
        if self.mesh_actor.actor.is_visible():
            self.mesh_actor.actor.set_visibility(False)
            if self.image_actor is None:
                self.image_actor = mlab.imshow(data.checkerboard())
            else:
                self.image_actor.actor.set_visibility(True)
        else:
            self.mesh_actor.actor.set_visibility(True)
            self.image_actor.actor.set_visibility(False)


if __name__ == "__main__":
    app = QApplication
