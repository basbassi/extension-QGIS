from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QVBoxLayout

class AltitudeDiffDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Altitude Différence")

        self.label1 = QLabel("Couche vecteur (points) :")
        self.comboPointLayer = QComboBox()

        self.label2 = QLabel("Couche raster :")
        self.comboRasterLayer = QComboBox()

        self.btnRun = QPushButton("Lancer le calcul")
        self.labelStatus = QLabel("")

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.comboPointLayer)
        layout.addWidget(self.label2)
        layout.addWidget(self.comboRasterLayer)
        layout.addWidget(self.btnRun)
        layout.addWidget(self.labelStatus)

        self.setLayout(layout)
