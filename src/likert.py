from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QRadioButton,
                             QWidget)
from PyQt5.QtGui import QFont


class LikertScale(QWidget):

    def __init__(self,
                 parent,
                 name="Likert Scale",
                 labels=["3", "2", "1", "0"]):
        super(LikertScale, self).__init__(parent)

        self.score = 3

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
        self.highest_button = QRadioButton()
        self.high_button = QRadioButton()
        self.low_button = QRadioButton()
        self.lowest_button = QRadioButton()

        self.highest_button.toggled.connect(lambda: self.on_selection(
            self.highest_button.isChecked(), value=3))
        self.high_button.toggled.connect(
            lambda: self.on_selection(self.high_button.isChecked(), value=2))
        self.low_button.toggled.connect(
            lambda: self.on_selection(self.low_button.isChecked(), value=1))
        self.lowest_button.toggled.connect(
            lambda: self.on_selection(self.lowest_button.isChecked(), value=0))

        # Add the labels and buttons to the h_layout
        h_layout.addWidget(highest)
        h_layout.addWidget(self.highest_button)
        h_layout.addWidget(high)
        h_layout.addWidget(self.high_button)
        h_layout.addWidget(low)
        h_layout.addWidget(self.low_button)
        h_layout.addWidget(lowest)
        h_layout.addWidget(self.lowest_button)

    def on_selection(self, checked, value):
        if checked:
            self.score = value
