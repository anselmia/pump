from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal
from Model.model import (
    messageBox,
    PumpListModel,
    HistListModel,
    PMListModel,
    BasicComboModel,
)
from Model.objects import Pump
from View.history import HistWindow
from View.pm import PMWindow


class PumpWindow(QMainWindow):

    window_closed = pyqtSignal()

    """Main Window."""

    def __init__(self, parent, *args, **kwargs):
        """Initializer."""
        super(PumpWindow, self).__init__(parent, *args, **kwargs)
        loadUi("UI/pump_manager.ui", self)

        self.datas = self.parent().datas
        self.resetView()

        self.initWidgets()

    def initWidgets(self):
        self.pumpmodel = PumpListModel(
            self.datas.pumps, self.datas.types, self.datas.locs
        )
        self.pumplist.setModel(self.pumpmodel)

        self.historymodel = HistListModel([], self.datas.locs)
        self.loclist.setModel(self.historymodel)

        self.pmmodel = PMListModel([], self.datas.freqs)
        self.pmlist.setModel(self.pmmodel)

        self.typemodel = BasicComboModel(self.datas.types)
        self.typecombo.setModel(self.typemodel)

        self.addbutton.clicked.connect(self.addpumpclicked)
        self.modifbutton.clicked.connect(self.modifpumpclicked)
        self.cancelbutton.clicked.connect(self.cancelclicked)
        self.validatebutton.clicked.connect(self.validateclicked)
        self.managehistorybutton.clicked.connect(self.showLocHistory)
        self.managepmbutton.clicked.connect(self.showPmHistory)
        self.deletebutton.clicked.connect(self.deletepumpclicked)
        self.pumplist.selectionModel().currentChanged.connect(self.pumpselected)
        self.pumplist.clicked.connect(self.pumpclicked)
        self.typecombo.currentIndexChanged.connect(self.onCurrentIndexChanged)

    def showLocHistory(self):
        self.locwin = HistWindow(self.selectedPump, parent=self)
        self.locwin.window_closed.connect(self.update_loc)
        self.locwin.show()

    def showPmHistory(self):
        if len(self.selectedPump.lochistory) > 0:
            if self.typecombo.currentIndex() >= 0:
                if self.selectedPump.not_only_uninstalled():
                    self.selectedPump._set_instance_struc(self.datas.struct)
                    self.pmwin = PMWindow(self.selectedPump, parent=self)
                    self.pmwin.window_closed.connect(self.update_pm)
                    self.pmwin.show()
                else:
                    messageBox(
                        "Uninstalled Location",
                        "There can be only uninstalled location to manage pm",
                    )
            else:
                messageBox(
                    "Pump type selection error",
                    "Please select a pump type before to manage pm",
                )
        else:
            messageBox(
                "Missing location history",
                "Please add a location history before to manage pm",
            )

    def pumpselected(self, index):
        if len(self.pumplist.selectionModel().selection().indexes()) > 0:
            self.selectedPump = self.pumpmodel.getItem(index)

    def pumpclicked(self, index):
        if len(self.pumplist.selectionModel().selection().indexes()) > 0:
            self.selectedPump = self.pumpmodel.getItem(index)

    def addpumpclicked(self):
        self.actionToken = "Add"
        self.selectframe.hide()
        self.dataframe.show()
        self.typecombo.setCurrentIndex(-1)
        self.lineserial.setText("")
        self.historymodel.clear()
        self.pmmodel.clear()
        self.datas.pm = [pm for pm in self.datas.pm if pm.pump_id != 0]
        self.datas.history = [
            history for history in self.datas.history if history.pump_id != 0
        ]
        self.selectedPump = Pump(0, 0, "", [], ([], self.datas.struct))

    def modifpumpclicked(self):
        if self.selectedPump is not None:
            self.selectframe.hide()
            self.dataframe.show()
            self.actionToken = "Modif"
            self.showpump()
            self.typecombo.setEnabled(False)

    def deletepumpclicked(self):
        if len(self.pumplist.selectionModel().selection().indexes()) > 0:
            pms = self.selectedPump.pm.copy()
            hists = self.selectedPump.lochistory.copy()

            for rule in self.datas.rules:
                if rule.pump == self.selectedPump:
                    self.datas.rules.remove(rule)

            del_index = self.pumplist.selectionModel().selection().indexes()[0]
            self.pumpmodel.removeItem(del_index.row())
            self.datas.save_pump()

            for pm in pms:
                self.datas.pm.remove(pm)
            self.datas.save_pm()

            for hist in hists:
                self.datas.history.remove(hist)
            self.datas.save_history()

            self.selectedPump = None
        else:
            messageBox("Selection Error", "Please select a pump")

    def cancelclicked(self):
        self.resetView()
        if self.actionToken == "Add":
            if len(self.historymodel.items) > 0:
                for hist in self.datas.history:
                    if hist.pump_id == 0:
                        self.datas.history.remove(hist)
                self.datas.save_history()
            if len(self.pmmodel.items) > 0:
                for pm in self.datas.pm:
                    if pm.pump_id == 0:
                        self.datas.pm.remove(pm)
                self.datas.save_pm()

    def validateclicked(self):
        if (
            self.historymodel.rowCount() > 0
            and self.typecombo.currentIndex() >= 0
            and self.lineserial.text() != ""
        ):
            if self.actionToken == "Add":
                type = self.typemodel.getItem(self.typecombo.currentIndex())
                serial = self.lineserial.text()
                temp_pump = Pump(0, type, serial, [], ([], [])).exist(self.datas.pumps)
                if temp_pump is None:
                    added = self.addPump()
                    if added:
                        self.resetView()
                else:
                    messageBox(
                        "Existing pump",
                        "A pump with the serial {0} already exist.".format(serial),
                    )
            elif self.actionToken == "Modif":
                if self.selectedPump is not None:
                    self.modifyPump()
                    self.resetView()
        else:
            messageBox(
                "Missing Information", "Please review the missing information(s)"
            )

    def onCurrentIndexChanged(self, ix):
        if self.actionToken == "Add" and self.typecombo.currentIndex() >= 0:
            type = self.typemodel.getItem(self.typecombo.currentIndex())
            self.selectedPump.type = type

    def showpump(self):
        index = self.typecombo.findText(
            self.selectedPump.type.value, QtCore.Qt.MatchFixedString
        )
        if index >= 0:
            self.typecombo.setCurrentIndex(index)

        self.lineserial.setText(self.selectedPump.serial)

        self.historymodel = HistListModel(self.selectedPump.lochistory, self.datas.locs)
        self.loclist.setModel(self.historymodel)

        self.pmmodel = PMListModel(self.selectedPump.pm, self.datas.freqs)
        self.pmlist.setModel(self.pmmodel)

    def addPump(self):
        added = True
        newid = self.datas.get_new_id("pumps")

        type = self.typemodel.getItem(self.typecombo.currentIndex())
        serial = self.lineserial.text()
        pms = self.pmmodel.getAllItem()
        loc_history = self.historymodel.getAllItem()

        newpump = Pump(newid, type, serial, pms, (loc_history, self.datas.struct))

        if newpump.location_free(self.datas.pumps):
            self.pumpmodel.addItem(newpump)
            self.datas.save_pump()

            pm_added = False
            for pm in self.datas.pm:
                if pm.pump_id == 0:
                    pm.pump_id = newid
                    pm_added = True
            if pm_added:
                self.datas.save_pm()

            hist_added = False
            for hist in self.datas.history:
                if hist.pump_id == 0:
                    hist.pump_id = newid
                    hist_added = True
            if hist_added:
                self.datas.save_history()
        else:
            added = False
            messageBox(
                "Location not free",
                "A pump of the the same type as already been installed at this location. Please select an other location or unintalled the other one first",
            )

        return added

    def modifyPump(self):
        selectedSerial = self.selectedPump.serial
        for i, pump in enumerate(self.datas.pumps):
            if pump.serial == selectedSerial:
                self.datas.pumps[i].type = self.typemodel.getItem(
                    self.typecombo.currentIndex()
                )
                self.datas.pumps[i].serial = self.lineserial.text()
                self.datas.pumps[i].lochistory = (
                    self.historymodel.getAllItem(),
                    self.datas.struct,
                )
                self.datas.pumps[i].pm = self.pmmodel.getAllItem()
                self.pumpmodel.updateItem(i, self.datas.pumps[i])
                self.datas.save_pump()
                break

    def update_loc(self):
        self.historymodel = HistListModel(self.selectedPump.lochistory, self.datas.locs)
        self.loclist.setModel(self.historymodel)

    def update_pm(self):
        self.pmmodel = PMListModel(self.selectedPump.pm, self.datas.freqs)
        self.pmlist.setModel(self.pmmodel)

    def resetView(self):
        self.actionToken = ""
        self.selectframe.show()
        self.dataframe.hide()
        self.lineserial.setText("")
        self.typecombo.setCurrentIndex(0)
        self.typecombo.setEnabled(True)
        self.selectedPump = None

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()
