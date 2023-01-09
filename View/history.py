from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate, pyqtSignal
from Model.model import messageBox, HistListModel, BasicComboModel
from Model.objects import LocHistory, Utility
from datetime import date


class HistWindow(QMainWindow):
    """Location History Window"""

    window_closed = pyqtSignal()

    def __init__(self, pump, parent, *args, **kwargs):
        """Initializer."""
        super(HistWindow, self).__init__(parent, *args, **kwargs)
        loadUi("UI/history.ui", self)
        self.datas = self.parent().datas
        self.pump = pump
        self.resetView()

        self.initWidgets()

    def initWidgets(self):
        self.model = HistListModel(self.pump.lochistory, self.datas.locs)
        self.loclist.setModel(self.model)

        locs_in_struct_with_selected_pump_type = [
            struct.loc for struct in self.datas.struct if self.pump.type == struct.type
        ]
        locs_in_struct_with_selected_pump_type.append(
            next(loc for loc in self.datas.locs if loc.id == 1)
        )
        self.locmodel = BasicComboModel(locs_in_struct_with_selected_pump_type)
        self.loccombo.setModel(self.locmodel)

        self.addbutton.clicked.connect(self.addClicked)
        self.modifbutton.clicked.connect(self.modifClicked)
        self.deletebutton.clicked.connect(self.deleteClicked)
        self.cancelbutton.clicked.connect(self.cancelclicked)
        self.validatebutton.clicked.connect(self.validateclicked)
        self.loclist.selectionModel().selectionChanged.connect(self.historyselected)
        self.loclist.clicked.connect(self.historyclicked)

    def historyselected(self, index):
        if len(self.loclist.selectionModel().selection().indexes()) > 0:
            self.selectedHistory = self.model.getItem(index.indexes()[0])

    def historyclicked(self, index):
        if len(self.loclist.selectionModel().selection().indexes()) > 0:
            self.selectedHistory = self.model.getItem(index)

    def addClicked(self):
        self.actionToken = "Add"
        self.selectframe.hide()
        self.dataframe.show()
        self.loccombo.setCurrentIndex(0)
        self.locdate.setDate(QDate(date.today()))

    def modifClicked(self):
        if self.selectedHistory is not None:
            self.selectframe.hide()
            self.dataframe.show()
            self.actionToken = "Modif"
            self.showHistory()
            self.loccombo.setEnabled(False)

    def deleteClicked(self):
        if len(self.loclist.selectionModel().selection().indexes()) > 0:
            if len(self.model.items) > 1:
                del_index = self.loclist.selectionModel().selection().indexes()[0]
                self.model.removeItem(del_index.row())
                self.datas.history.remove(self.selectedHistory)
                self.datas.save_history()
                self.selectedHistory = None
            else:
                messageBox(
                    "Deletion Error", "There must be at least one location history"
                )
        else:
            messageBox("Selection Error", "Please select a location history")

    def cancelclicked(self):
        self.resetView()

    def validateclicked(self):
        if self.loccombo.currentIndex() >= 0:
            selected_loc = self.locmodel.getItem(self.loccombo.currentIndex())

            if self.actionToken == "Add":
                temp_hist = LocHistory(
                    0,
                    self.pump.id,
                    selected_loc,
                    Utility.qdate_to_str(self.locdate.date()),
                )
                hist_in_pump = temp_hist.exist(self.pump.lochistory)
                if hist_in_pump is None:
                    lastloc = self.pump.get_actual_loc()
                    newloc = self.datas.loc(self.loccombo.currentText())
                    if lastloc is None or lastloc != newloc:
                        self.addHistory()
                        self.resetView()
                    else:
                        messageBox(
                            "New location error",
                            "New location must be different from previous loc !",
                        )
                else:
                    messageBox(
                        "Existing History",
                        "This pump has already been installed at this date.",
                    )
            elif self.actionToken == "Modif":
                if self.selectedHistory is not None:
                    self.modifyHistory()
                    self.resetView()
        else:
            messageBox(
                "Missing Information", "Please review the missing information(s)"
            )

    def showHistory(self):
        self.locdate.setDate(QDate(self.selectedHistory.date))
        loc_value = self.selectedHistory.loc.value
        index = self.loccombo.findText(loc_value, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.loccombo.setCurrentIndex(index)

    def addHistory(self):
        newid = self.datas.get_new_id("history")
        loc = self.locmodel.getItem(self.loccombo.currentIndex())
        date = Utility.qdate_to_str(self.locdate.date())
        lochistory = LocHistory(newid, self.pump.id, loc, date)
        self.datas.history.append(lochistory)
        self.model.addItem(lochistory)
        self.datas.save_history()

    def modifyHistory(self):
        id = self.selectedHistory.id
        loc = self.selectedHistory.loc
        date = Utility.qdate_to_str(self.locdate.date())
        temp_hist = LocHistory(id, self.pump.id, loc, date)

        for i, hist in enumerate(self.pump.lochistory):
            if hist.id == temp_hist.id:
                self.model.updateItem(i, temp_hist)
                break

        for i, hist in enumerate(self.datas.history):
            if hist.id == temp_hist.id:
                self.datas.history[i] = temp_hist
                break

        self.datas.save_history()

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()

    def resetView(self):
        self.selectedHistory = None
        self.actionToken = ""
        self.dataframe.hide()
        self.selectframe.show()
        self.loccombo.setEnabled(True)
