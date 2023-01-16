#!/usr/bin/env python

from src.likert import LikertScale
from PyQt5.QtWidgets import QWidget, QApplication

app = QApplication([])
wid = QWidget()
likert = LikertScale(parent=wid, name="Test")
wid.show()
app.exec()
