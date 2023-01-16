from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QRadioButton,
                             QWidget)
from PyQt5.QtGui import QFont


class LikertScale(QWidget):

    def __init__(self,
                 parent,
                 name="Likert Scale",
                 labels=["3", "2", "1", "0"]):
        super(LikertScale, self).__init__(parent)

        title = QLabel(name)
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        v_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout()

        v_layout.addWidget(title)
        v_layout.addLayout(h_layout)

        # Create labels for the Likert scale options
        highest = QLabel(labels[0])
        high = QLabel(labels[1])
        low = QLabel(labels[2])
        lowest = QLabel(labels[3])

        # Create radio buttons for the Likert scale options
        highest_button = QRadioButton()
        high_button = QRadioButton()
        low_button = QRadioButton()
        lowest_button = QRadioButton()

        highest_button.toggled.connect(
            lambda: self.on_selection(highest_button.isChecked(), val=3))
        high_button.toggled.connect(
            lambda: self.on_selection(high_button.isChecked(), val=2))
        low_button.toggled.connect(
            lambda: self.on_selection(low_button.isChecked(), val=1))
        lowest_button.toggled.connect(
            lambda: self.on_selection(lowest_button.isChecked(), val=0))

        # Add the labels and buttons to the h_layout
        h_layout.addWidget(highest)
        h_layout.addWidget(highest_button)
        h_layout.addWidget(high)
        h_layout.addWidget(high_button)
        h_layout.addWidget(low)
        h_layout.addWidget(low_button)
        h_layout.addWidget(lowest)
        h_layout.addWidget(lowest_button)

    def on_selection(self, checked, val):
        if checked:
            print("Current value: ", val)
