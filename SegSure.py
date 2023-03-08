#!/usr/bin/env python

import sys

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QPushButton, QHBoxLayout, QVBoxLayout, QLabel,
                             QCheckBox, QComboBox, QApplication, QWidget,
                             QFrame)
import nibabel as nib
from skimage.measure import marching_cubes
from src.dataloader import DataLoader
from src.filedialog import SelectPathsDialog
from src.segviewer import SegmentationViewer
from src.likert import LikertScale


class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.idx = -1
        self.pid = 0

        self.viewer = SegmentationViewer(self)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        files_dialog = SelectPathsDialog(self)

        prev_button = QPushButton("Prev", self)
        next_button = QPushButton("Next", self)
        seg_button = QPushButton("View Seg", self)

        prev_button.setShortcut("p")
        next_button.setShortcut("n")
        seg_button.setShortcut("q")

        # Connect the buttons to their respective functions
        prev_button.clicked.connect(self.prev_button_clicked)
        next_button.clicked.connect(self.next_button_clicked)
        seg_button.clicked.connect(self.seg_button_clicked)

        button_layout = QHBoxLayout()
        button_layout.addWidget(prev_button)
        button_layout.addWidget(next_button)
        button_layout.addWidget(seg_button)

        # Create labels
        font = QtGui.QFont()
        font.setPointSize(26)
        self.tlv_label = QLabel("TLV:", self)
        self.tav_label = QLabel("TAV:", self)
        self.tac_label = QLabel("TAC:", self)

        self.tlv_label.setFont(font)
        self.tav_label.setFont(font)
        self.tac_label.setFont(font)

        label_layout = QHBoxLayout()
        label_layout.addWidget(self.tlv_label)
        label_layout.addWidget(self.tav_label)
        label_layout.addWidget(self.tac_label)

        # Create checkboxes
        self.error_checkbox = QCheckBox("Error", self)
        self.reviewed_checkbox = QCheckBox("Reviewed", self)
        self.inspect_checkbox = QCheckBox("Inspect", self)
        self.error_checkbox.setFont(font)
        self.reviewed_checkbox.setFont(font)
        self.inspect_checkbox.setFont(font)

        self.error_checkbox.setShortcut("e")
        self.reviewed_checkbox.setShortcut("r")
        self.inspect_checkbox.setShortcut("i")

        self.error_checkbox.stateChanged.connect(self.err_box_checked)
        self.reviewed_checkbox.stateChanged.connect(self.rev_box_checked)
        self.inspect_checkbox.stateChanged.connect(self.inspect_checked)

        # Create the combobox and add options
        self.reason_combobox = QComboBox(self)
        self.reason_combobox.addItem("Discontinuous")
        self.reason_combobox.addItem("Leak")
        self.reason_combobox.addItem("Expiratory")
        self.reason_combobox.addItem("Other")
        self.reason_combobox.setFont(font)

        self.scale_leaks = LikertScale(
            self, "Detected Leaks",
            ["None", "Small", "Multiple/Medium", "Major"])
        self.scale_segmental = LikertScale(
            self, "Segmental Branches",
            ["All", "1 Missing", ">2 missing", "Lobe(s) missing"])
        self.scale_subseg = LikertScale(
            self, "Segmentation Extent",
            ["Complete", "Almost Complete", "Partial", "Incomplete"])

        likert_layout = QHBoxLayout()
        likert_layout.addWidget(self.scale_leaks)

        # Create a line separator
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        likert_layout.addWidget(line)

        likert_layout.addWidget(self.scale_segmental)

        # Create a line separator
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        likert_layout.addWidget(line)

        likert_layout.addWidget(self.scale_subseg)

        # Add the checkboxes and combobox to the layout
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.error_checkbox)
        checkbox_layout.addWidget(self.reviewed_checkbox)
        checkbox_layout.addWidget(self.inspect_checkbox)
        checkbox_layout.addWidget(self.reason_combobox)
        checkbox_layout.addWidget(files_dialog)

        # Arrange layout
        vblayout = QVBoxLayout(self)
        vblayout.addWidget(self.viewer)
        vblayout.addLayout(button_layout)
        vblayout.addLayout(label_layout)
        vblayout.addLayout(checkbox_layout)
        vblayout.addLayout(likert_layout)

        self.showMaximized()

    def load_case(self, increment: bool):

        def _load_image():
            pid = str(self.pid)
            if any(pid in s for s in self.revdata.image_list):
                matching = [s for s in self.revdata.image_list if pid in s]
                image_path = matching[0]
                self.viewer.setPhoto(QtGui.QPixmap(image_path))
            else:
                print(f"{pid} segmentation image not found")

        def _load_values():

            def _get_color(value, min_range, max_range):
                if value < min_range or value > max_range:
                    return "red"
                else:
                    return "black"

            tlv = self.revdata.flagged_df.at[self.idx, 'bp_tlv']
            tav = self.revdata.flagged_df.at[self.idx, 'bp_airvol']
            tac = self.revdata.flagged_df.at[self.idx, 'bp_tcount']

            err = self.revdata.flagged_df.at[self.idx, 'bp_seg_error']
            rev = self.revdata.flagged_df.at[self.idx, 'bp_reviewed']

            tlv_col = _get_color(tlv, 3.5, 8.0)
            tav_col = _get_color(tav, 0.08, 0.4)
            tac_col = _get_color(tac, 150, 400)

            self.tlv_label.setText(f"TLV: {tlv}")
            self.tav_label.setText(f"TAV: {tav}")
            self.tac_label.setText(f"TAC: {tac}")

            self.tlv_label.setStyleSheet(f"color: {tlv_col};")
            self.tav_label.setStyleSheet(f"color: {tav_col};")
            self.tac_label.setStyleSheet(f"color: {tac_col};")

            if err == 1:
                self.error_checkbox.setChecked(True)
            else:
                self.error_checkbox.setChecked(False)

            if rev == 1:
                self.reviewed_checkbox.setChecked(True)
            else:
                self.reviewed_checkbox.setChecked(False)

            self.scale_leaks.highest_button.setChecked(True)
            self.scale_segmental.highest_button.setChecked(True)
            self.scale_subseg.highest_button.setChecked(True)

        def _set_values():
            if self.idx == -1:
                print("Starting Review")
                return

            if self.error_checkbox.isChecked():
                self.revdata.flagged_df.at[
                    self.idx,
                    'bp_err_reason'] = self.reason_combobox.currentText()

            if not self.reviewed_checkbox.isChecked():
                self.reviewed_checkbox.setChecked(True)

            self.revdata.flagged_df.at[
                self.idx, 'bp_leak_score'] = self.scale_leaks.score
            self.revdata.flagged_df.at[
                self.idx, 'bp_segmental_score'] = self.scale_segmental.score
            self.revdata.flagged_df.at[
                self.idx, 'bp_subsegmental_score'] = self.scale_subseg.score

        def _get_pid(increment):
            if increment:
                self.idx += 1
            else:
                self.idx -= 1
            if self.idx >= self.revdata.flagged_df.shape[0]:
                self.idx = 0
            elif self.idx < 0:
                self.idx = self.revdata.flagged_df.shape[0] - 1

            if self.idx % 10 == 0:
                self.revdata.save_flagged_df()
                print(f"Saved review csv. List id {self.idx}")

            pt_id = self.revdata.flagged_df.at[self.idx, "participant_id"]
            return pt_id

        _set_values()
        self.pid = _get_pid(increment)
        _load_image()
        _load_values()

    def prev_button_clicked(self):
        self.load_case(False)

    def next_button_clicked(self):
        self.load_case(True)

    def seg_button_clicked(self):
        if 'mlab' not in sys.modules:
            from mayavi import mlab
        matching = [s for s in self.revdata.seg_list if str(self.pid) in s]
        seg_arr = nib.load(f"{matching[0]}").get_fdata()
        verts, faces, norms, vals = marching_cubes(seg_arr, 0)
        mlab.triangular_mesh(verts[:, 0], verts[:, 1], verts[:, 2], faces)
        mlab.show()

    def load_data(self, path_list):
        self.revdata = DataLoader(path_list[0], path_list[1], path_list[2])
        print("Data Loaded")

    def err_box_checked(self, state):
        if state == QtCore.Qt.Checked:
            self.revdata.flagged_df.at[self.idx, "bp_seg_error"] = 1
        else:
            self.revdata.flagged_df.at[self.idx, "bp_seg_error"] = 0

    def rev_box_checked(self, state):
        if state == QtCore.Qt.Checked:
            self.revdata.flagged_df.at[self.idx, "bp_reviewed"] = 1
        else:
            self.revdata.flagged_df.at[self.idx, "bp_reviewed"] = 0

    def inspect_checked(self, state):
        if state == QtCore.Qt.Checked:
            self.revdata.flagged_df.at[self.idx, "bp_inspect"] = 1
        else:
            self.revdata.flagged_df.at[self.idx, "bp_inspect"] = 0

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_E:
            self.error_checkbox.toggle()
        elif event.key() == QtCore.Qt.Key_R:
            self.reviewed_checkbox.toggle()
        elif event.key() == QtCore.Qt.Key_I:
            self.inspect_checkbox.toggle()
        elif event.key() == QtCore.Qt.Key_P:
            self.prev_button_clicked()
        elif event.key() == QtCore.Qt.Key_N:
            self.next_button_clicked()
        elif event.key() == QtCore.Qt.Key_3:
            self.scale_leaks.lowest_button.setChecked(True)
        elif event.key() == QtCore.Qt.Key_2:
            self.scale_leaks.low_button.setChecked(True)
        elif event.key() == QtCore.Qt.Key_1:
            self.scale_leaks.high_button.setChecked(True)
        elif event.key() == QtCore.Qt.Key_6:
            self.scale_segmental.lowest_button.setChecked(True)
        elif event.key() == QtCore.Qt.Key_5:
            self.scale_segmental.low_button.setChecked(True)
        elif event.key() == QtCore.Qt.Key_4:
            self.scale_segmental.high_button.setChecked(True)
        elif event.key() == QtCore.Qt.Key_9:
            self.scale_subseg.lowest_button.setChecked(True)
        elif event.key() == QtCore.Qt.Key_8:
            self.scale_subseg.low_button.setChecked(True)
        elif event.key() == QtCore.Qt.Key_7:
            self.scale_subseg.high_button.setChecked(True)
        elif event.key() == QtCore.Qt.Key_0:
            self.scale_leaks.highest_button.setChecked(True)
            self.scale_segmental.highest_button.setChecked(True)
            self.scale_subseg.highest_button.setChecked(True)
        elif event.key() == QtCore.Qt.Key_D:
            self.reason_combobox.setCurrentIndex(0)
        elif event.key() == QtCore.Qt.Key_X:
            self.reason_combobox.setCurrentIndex(2)
        elif event.key() == QtCore.Qt.Key_O:
            self.reason_combobox.setCurrentIndex(3)
        elif event.key() == QtCore.Qt.Key_L:
            self.reason_combobox.setCurrentIndex(1)


if __name__ == '__main__':
    app = QApplication([])
    app.setApplicationName("Segment Sure")
    reviewer = MainWindow()
    # reviewer = QLabel("Hello World")
    reviewer.show()
    app.exec()
