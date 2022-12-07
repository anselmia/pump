#this program intend to follow PM for PTS Pumps

import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from model import Data, TablePumpModel
from pumps_window import PumpWindow


class MainWindow(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super(MainWindow, self).__init__()
        loadUi("main.ui", self)
        self.datas = Data()
        self.model = TablePumpModel(self.datas)
        self.pumptable.setModel(self.model)

        self.actionManage.triggered.connect(self.access_windows_pump)

    def access_windows_pump(self):
        self.pumpwin = PumpWindow(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()  
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(win)
    widget.show()

    sys.exit(app.exec_())