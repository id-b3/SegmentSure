#!/usr/bin/env python
# coding: utf-8

from pathlib import Path

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene,
                             QGraphicsPixmapItem, QFrame, QPushButton,
                             QHBoxLayout, QVBoxLayout, QLabel, QCheckBox,
                             QComboBox, QApplication, QFileDialog, QWidget,
                             QMessageBox)
import nibabel as nib
import pandas as pd
from mayavi import mlab
from skimage.measure import marching_cubes


class DataLoader():

    def __init__(self, image_dir: str, seg_dir: str, summary_path: str):
        """
        Loads the images, segmentations and summary dataframes.
        :param image_dir str: Path containing segmentation images.
        :param seg_dir str: Path containing nifti format segmentations.
        :param summary_path str: Summary csv path.
        """
        self.image_list = [i for i in Path(image_dir).iterdir() if i.is_file()]
        self.summary_df = pd.read_csv(summary_path)
        self.seg_list = [s for s in Path(seg_dir).iterdir() if s.is_file()]

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
        self.flagged_df.reset_index(drop=True, inplace=True)

    def get_random_sample(self, number: int = 100):
        """
        Returns n random segmentations
        """
        self.random_df = self.summary_df.sample(number)
        self.random_df.reset_index(drop=True, inplace=True)


class SelectPathsDialog(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        # Create buttons to select the paths
        self.images_button = QPushButton("Select Images Folder")
        self.segmentations_button = QPushButton("Select Segmentations Folder")
        self.csv_button = QPushButton("Select CSV File")
        self.confirm_button = QPushButton("Confirm and Exit")

        # Create labels to display the selected paths
        self.images_label = QLabel("No folder selected")
        self.segmentations_label = QLabel("No folder selected")
        self.csv_label = QLabel("No file selected")

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.images_button)
        layout.addWidget(self.images_label)
        layout.addWidget(self.segmentations_button)
        layout.addWidget(self.segmentations_label)
        layout.addWidget(self.csv_button)
        layout.addWidget(self.csv_label)
        layout.addWidget(self.confirm_button)
        self.setLayout(layout)

        # Connect the buttons to their respective functions
        self.images_button.clicked.connect(self.select_images_folder)
        self.segmentations_button.clicked.connect(
            self.select_segmentations_folder)
        self.csv_button.clicked.connect(self.select_csv_file)
        self.confirm_button.clicked.connect(self.confirm_and_exit)

    def select_images_folder(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        folder = QFileDialog.getExistingDirectory(self,
                                                  "Select Images Folder",
                                                  options=options)
        if folder:
            # Save the selected folder to a class variable
            self.images_folder = folder
            # Update the label to display the selected folder
            self.images_label.setText(folder)

    def select_segmentations_folder(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        folder = QFileDialog.getExistingDirectory(
            self, "Select Segmentations Folder", options=options)
        if folder:
            # Save the selected folder to a class variable
            self.segmentations_folder = folder
            # Update the label to display the selected folder
            self.segmentations_label.setText(folder)

    def select_csv_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)",
            options=options)
        if file:
            # Save the selected file to a class variable
            self.csv_file = file
            # Update the label to display the selected file
            self.csv_label.setText(file)

    def confirm_and_exit(self):
        try:
            self.parent.load_data(
                [self.images_folder, self.segmentations_folder, self.csv_file])
            self.hide()
        except Exception as e:
            # create an error message box
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(
                f"{str(e)} \n\n Please select correct folders and csv file.")
            msg.setWindowTitle("Error")
            msg.exec_()


class PhotoViewer(QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
            self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0


class SegReviewer(QWidget):

    def __init__(self):
        super(SegReviewer, self).__init__()

        self.idx = 0

        self.viewer = PhotoViewer(self)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        files_dialog = SelectPathsDialog(self)

        prev_button = QPushButton("Prev", self)
        next_button = QPushButton("Next", self)
        seg_button = QPushButton("View Seg", self)

        prev_button.setShortcut("p")
        next_button.setShortcut("n")
        seg_button.setShortcut("s")

        # Connect the buttons to their respective functions
        prev_button.clicked.connect(self.prev_button_clicked)
        next_button.clicked.connect(self.next_button_clicked)
        seg_button.clicked.connect(self.seg_button_clicked)

        button_layout = QHBoxLayout()
        button_layout.addWidget(prev_button)
        button_layout.addWidget(next_button)
        button_layout.addWidget(seg_button)

        # Create labels
        self.tlv_label = QLabel("TLV:", self)
        self.tav_label = QLabel("TAV:", self)
        self.tac_label = QLabel("TAC:", self)

        label_layout = QHBoxLayout()
        label_layout.addWidget(self.tlv_label)
        label_layout.addWidget(self.tav_label)
        label_layout.addWidget(self.tac_label)

        # Create checkboxes
        self.error_checkbox = QCheckBox("Error", self)
        self.reviewed_checkbox = QCheckBox("Reviewed", self)

        self.error_checkbox.setShortcut("e")
        self.reviewed_checkbox.setShortcut("r")

        # Create the combobox and add options
        reason_combobox = QComboBox(self)
        reason_combobox.addItem("Discontinuous")
        reason_combobox.addItem("Leak")
        reason_combobox.addItem("Expiratory")
        reason_combobox.addItem("Other")

        # Add the checkboxes and combobox to the layout
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(error_checkbox)
        checkbox_layout.addWidget(reviewed_checkbox)
        checkbox_layout.addWidget(reason_combobox)
        checkbox_layout.addWidget(files_dialog)

        # Arrange layout
        VBlayout = QVBoxLayout(self)
        VBlayout.addWidget(self.viewer)
        VBlayout.addLayout(button_layout)
        VBlayout.addLayout(label_layout)
        VBlayout.addLayout(checkbox_layout)

        self.showMaximized()

    def load_case(self, increment: bool):

        def _load_image(pid):
            pid = str(int(pid))
            if any(pid in s for s in self.revdata.image_list):
                matching = [s for s in self.revdata.image_list if pid in s]
                image_path = f"./Segmentation_Check/{matching[0]}"
                self.viewer.setPhoto(QtGui.QPixmap(image_path))
            else:
                print(f"{pid} segmentation image not found")

        def _load_values(pid):

            def _get_color(value, min_range, max_range):
                if value < min_range or value > max_range:
                    return "red"
                else:
                    return "black"

            pid = str(int(pid))
            tlv = self.revdata.flagged_df.iloc[self.idx]['bp_tlv']
            tav = self.revdata.flagged_df.iloc[self.idx]['bp_airvol']
            tac = self.revdata.flagged_df.iloc[self.idx]['bp_tcount']

            tlv_col = _get_color(tlv, 3.5, 8.0)
            tav_col = _get_color(tav, 0.08, 0.4)
            tac_col = _get_color(tac, 150, 400)

            self.tlv_label.setText(f"TLV: {tlv}")
            self.tav_label.setText(f"TAV: {tav}")
            self.tac_label.setText(f"TAC: {tac}")

            self.tlv_label.setStyleSheet(f"color: {tlv_col};")
            self.tlv_label.setStyleSheet(f"color: {tav_col};")
            self.tlv_label.setStyleSheet(f"color: {tac_col};")

        def _get_pid(increment):
            if increment:
                self.idx += 1
            else:
                self.idx -= 1
            if abs(self.idx) >= self.revdata.flagged_df.shape[0]:
                self.idx = 0
            pt_id = self.revdata.flagged_df.at(self.idx, "participant_id")
            return pt_id

        pid = _get_pid(increment)
        _load_image(pid)
        _load_values(pid)

    def prev_button_clicked(self):
        self.load_case(True)

    def next_button_clicked(self):
        self.load_case(False)

    def seg_button_clicked(self):
        seg_arr = nib.load("segmentation.nii.gz").get_fdata()
        verts, faces, norms, vals = marching_cubes(seg_arr, 0)
        mlab.triangular_mesh(verts[:, 0], verts[:, 1], verts[:, 2], faces)
        mlab.show()

    def load_data(self, path_list):
        self.revdata = DataLoader(path_list[0], path_list[1], path_list[2])
        print("Data Loaded")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_E:
            self.error_checkbox.toggle()
        elif event.key() == QtCore.Qt.Key_R:
            self.reviewed_checkbox.toggle()
        elif event.key() == QtCore.Qt.Key_P:
            self.prev_button_clicked()
        elif event.key() == QtCore.Qt.Key_N:
            self.next_button_clicked()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    reviewer = SegReviewer()
    reviewer.show()
    sys.exit(app.exec_())
