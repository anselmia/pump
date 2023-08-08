import sys
import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QVBoxLayout, QWidget, QTableView
from PyQt5 import uic
from Model.model import TablePumpModel, ColorProxy
from Model.objects import Data, Location, Type
from View.pumps_window import PumpWindow
from View.location import LocWindow
from View.structure import StructWindow
from View.type import TypeWindow
from View.frequency import FreqWindow
from View.rules import RulesWindow
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from config import data_dir

class MainWindow(QMainWindow):
    """Main Window."""

    def __init__(self, data_dir_overloaded=None, parent=None):
        """Initializer."""
        super(MainWindow, self).__init__()

        file_path = r'\\f01.goiba.net\Common\zz_Struct\19_Maintenance_Plan\17-PMs\2-PUMPS Follow up\Pump pm follow up software\UI\main.ui'

        if not os.path.exists(file_path):
            print("File does not exist!")
            return

        uic.loadUi(file_path, self)
        
        if data_dir_overloaded is not None:
            self.datas = Data(data_dir_overloaded)
        else:
            self.datas = Data(data_dir)

        # Get the index of the existing pumptable in its current layout
        index = self.layout().indexOf(self.pumptable)

        # Remove the existing pumptable from its current layout
        self.pumptable.setParent(None)

        # Create a new container widget and layout
        container = QWidget()
        layout = QVBoxLayout(container)

        # Create an instance of TablePumpModel and ColorProxy
        self.model = TablePumpModel(self.datas)
        self.proxy = ColorProxy()
        self.proxy.setSourceModel(self.model)    

        # Create a new pumptable widget and set the model
        new_pumptable = QTableView()
        new_pumptable.setModel(self.proxy)

        # Set any additional properties for the new pumptable
        # ...

        # Add the new pumptable to the layout
        layout.addWidget(new_pumptable)

        # Set the new container widget as the central widget of the main window
        self.setCentralWidget(container)

        # Set the new pumptable widget as the reference for further operations
        self.pumptable = new_pumptable

        self.pumpwin = None

        header = self.pumptable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        header = self.pumptable.verticalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        self.actionManage.triggered.connect(self.manage_pump)
        self.actionLocation.triggered.connect(self.manage_location)
        self.actionType.triggered.connect(self.manage_type)
        self.actionFrequency.triggered.connect(self.manage_frequency)
        self.actionStructure.triggered.connect(self.manage_structure)
        self.actionRules.triggered.connect(self.manage_rules)
        self.pumptable.doubleClicked.connect(self.show_pump)

        self.resize_table_to_contents()

    def show_pump(self, index):
        col = index.column()
        pump_str_array = self.model.headerData(
            col, QtCore.Qt.Horizontal, role=Qt.DisplayRole
        ).rsplit("_", 1)
        pump_location = pump_str_array[0]
        pump_type = pump_str_array[1]

        pump_location_id = Location.get_id_from_value(pump_location, self.datas.locs)
        pump_type_id = Type.get_id_from_value(pump_type, self.datas.types)
        selected_pump = next(
            (
                pump
                for pump in self.datas.pumps
                if pump.type.id == pump_type_id
                and pump.get_actual_loc().id == pump_location_id
            ),
            None,
        )

        if selected_pump is not None:
            if self.pumpwin is not None and self.pumpwin.isVisible():
                self.pumpwin.close()

            self.pumpwin = PumpWindow(parent=self)
            index_in_pump_list = self.datas.pumps.index(selected_pump)
            self.pumpwin.window_closed.connect(self.update_table)
            qindex = self.pumpwin.pumpmodel.index(index_in_pump_list, 0)

            self.pumpwin.pumplist.setCurrentIndex(qindex)
            self.pumpwin.modifbutton.click()
            self.pumpwin.show()

    def manage_pump(self):
        self.pumpwin = PumpWindow(parent=self)
        self.pumpwin.window_closed.connect(self.update_table)
        self.pumpwin.show()

    def manage_location(self):
        self.locwin = LocWindow(parent=self)
        self.locwin.setWindowTitle("Location")
        self.locwin.exec_()

    def manage_type(self):
        self.typewin = TypeWindow(parent=self)
        self.typewin.setWindowTitle("Type")
        self.typewin.exec_()

    def manage_frequency(self):
        self.freqwin = FreqWindow(parent=self)
        self.freqwin.setWindowTitle("Frequency")
        self.freqwin.exec_()

    def manage_structure(self):
        self.structwin = StructWindow(parent=self)
        self.structwin.window_closed.connect(self.update_table)
        self.structwin.exec_()

    def manage_rules(self):
        self.rulestwin = RulesWindow(parent=self)
        self.rulestwin.window_closed.connect(self.update_table)
        self.rulestwin.exec_()

    def update_table(self):
        self.model = TablePumpModel(self.datas)
        self.proxy.setSourceModel(self.model)
        self.pumptable.setModel(self.proxy)
        self.resize_table_to_contents()

    def resize_table_to_contents(self):
        vh = self.pumptable.verticalHeader()
        hh = self.pumptable.horizontalHeader()
        size = QtCore.QSize(
            hh.length(), vh.length()
        )  # Get the length of the headers along each axis.
        size += QtCore.QSize(
            vh.size().width(), hh.size().height()
        )  # Add on the lengths from the *other* header
        size += QtCore.QSize(5, 45)  # Extend further so scrollbars aren't shown.
        self.resize(size)

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    win.resize_table_to_contents()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()