from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
import os
from mayavi.mlab import triangular_mesh

from pyface.qt import QtGui
from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, SceneEditor

from skimage import measure
import nibabel as nib
import time
os.environ['ETS_TOOLKIT'] = 'qt4'


class Visualization(HasTraits):
    scene = Instance(MlabSceneModel, ())

    @on_trait_change('scene.activated')
    def update_plot(self):
        # PLot to Show
        array = nib.load("segmentation.nii.gz").get_fdata()
        # Use marching cubes to generate a surface mesh
        vertices, faces, normals, values = measure.marching_cubes(
            array, 0, allow_degenerate=False, step_size=1)

        obj = triangular_mesh(vertices[:, 0],
                              vertices[:, 1],
                              vertices[:, 2],
                              faces,
                              color=(1, 1, 1))

    view = View(Item('scene',
                     editor=SceneEditor(scene_class=MayaviScene),
                     height=250,
                     width=300,
                     show_label=False),
                resizable=True)


class MayaviQWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.visualization = Visualization()

        self.ui = self.visualization.edit_traits(parent=self,
                                                 kind='subpanel').control
        layout.addWidget(self.ui)
        self.ui.setParent(self)


class Ui_MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Create the Prev and Next buttons
        self.prev_button = QPushButton("Prev")
        self.next_button = QPushButton("Next")

        # Create the widget that will span the entire window width
        container = QtGui.QWidget()
        mayavi_widget = MayaviQWidget(container)

        # Create the TLV, TAV, and TAC labels
        self.tlv_label = QLabel("TLV")
        self.tav_label = QLabel("TAV")
        self.tac_label = QLabel("TAC")

        # Create the layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)

        # Create the layout for the
        # Create the layout for the labels
        label_layout = QHBoxLayout()
        label_layout.addWidget(self.tlv_label)
        label_layout.addWidget(self.tav_label)
        label_layout.addWidget(self.tac_label)

        # Create the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(mayavi_widget)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(label_layout)

        # Set the main layout for the main window
        self.setLayout(main_layout)


if __name__ == "__main__":
    import sys
    tic = time.perf_counter()
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = Ui_MainWindow()
    toc = time.perf_counter()
    print(f"Total time: {toc - tic:0.4f} seconds")
    window.show()
    sys.exit(app.exec_())
