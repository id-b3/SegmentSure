from PyQt5.QtWidgets import (QPushButton, QLabel, QVBoxLayout, QWidget,
                             QFileDialog, QMessageBox)


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
        self.paths = ["", "", ""]

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
            self.paths = [
                self.images_folder, self.segmentations_folder, self.csv_file
            ]
            self.parent.load_data(self.paths)
            self.hide()
        except Exception as e:
            # create an error message box
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(
                f"{str(e)} \n\n Please select correct folders and csv file.")
            msg.setWindowTitle("Error")
            msg.exec_()
