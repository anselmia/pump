from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate, pyqtSignal
from Model.model import messageBox, PMListModel, BasicComboModel
from Model.objects import Structure, PM, Utility
from datetime import date


class PMWindow(QMainWindow):
    """PM Window"""

    window_closed = pyqtSignal()

    def __init__(self, pump, parent, *args, **kwargs):
        """Initializer."""
        super(PMWindow, self).__init__(parent, *args, **kwargs)
        loadUi("UI/pm.ui", self)
        self.datas = self.parent().datas
        self.pump = pump
        self.resetView()

        self.initWidgets()

    def initWidgets(self):
        self.model = PMListModel(self.pump.pm, self.datas.freqs)
        self.pmlist.setModel(self.model)

        actualLoc = self.pump.get_actual_loc()

        if actualLoc.id == "1":
            SelectedFreqs = self.datas.freqs
        else:
            SelectedFreqs = (
                Structure(actualLoc, self.pump.type, [], [])
                .exist(self.datas.struct)
                .freqs
            )

        self.freqmodel = BasicComboModel(SelectedFreqs)
        self.freqcombo.setModel(self.freqmodel)

        self.addbutton.clicked.connect(self.addpmclicked)
        self.modifbutton.clicked.connect(self.modifpmclicked)
        self.deletebutton.clicked.connect(self.deletepmclicked)
        self.cancelbutton.clicked.connect(self.cancelclicked)
        self.validatebutton.clicked.connect(self.validateclicked)
        self.pmlist.selectionModel().selectionChanged.connect(self.pmselected)
        self.pmlist.clicked.connect(self.pmclicked)

    def pmselected(self, index):
        if len(self.pmlist.selectionModel().selection().indexes()) > 0:
            self.selectedpm = self.model.getItem(index.indexes()[0])

    def pmclicked(self, index):
        if len(self.pmlist.selectionModel().selection().indexes()) > 0:
            self.selectedpm = self.model.getItem(index)

    def addpmclicked(self):
        self.actionToken = "Add"
        self.selectframe.hide()
        self.dataframe.show()
        self.freqcombo.setCurrentIndex(0)
        self.pmdate.setDate(QDate(date.today()))
        self.comtext.setPlainText("")

    def modifpmclicked(self):
        if self.selectedpm is not None:
            self.selectframe.hide()
            self.dataframe.show()
            self.actionToken = "Modif"
            self.freqcombo.setEnabled(False)
            self.showPm()

    def deletepmclicked(self):
        if len(self.pmlist.selectionModel().selection().indexes()) > 0:
            del_index = self.pmlist.selectionModel().selection().indexes()[0]
            selected_struct = self.pump.struct
            associated_freqs = selected_struct.freqs_id_associated[
                self.selectedpm.freq.id
            ]
            associated_pm = self.pump.get_associated_pm(
                self.selectedpm, associated_freqs
            )

            for pm_to_del in associated_pm:
                for i, pm in enumerate(self.pump.pm):
                    if pm.id == pm_to_del.id:
                        self.model.removeItem(i)
                        self.datas.pm.remove(pm_to_del)
                        break

            pm = next(pm for pm in self.datas.pm if pm.id == self.selectedpm.id)
            self.model.removeItem(del_index.row())
            self.datas.pm.remove(pm)

            self.datas.save_pm()
            self.selectedpm = None
        else:
            messageBox("Selection Error", "Please select a pm")

    def cancelclicked(self):
        self.resetView()

    def validateclicked(self):
        if self.freqcombo.currentIndex() >= 0:
            selected_freq = self.freqmodel.getItem(self.freqcombo.currentIndex())
            if self.actionToken == "Add":
                pm = PM(
                    "0",
                    self.pump.id,
                    selected_freq,
                    Utility.qdate_to_str(self.pmdate.date()),
                    "",
                )
                freq_in_pm = pm.exist(self.pump.pm)
                if freq_in_pm is None:
                    self.addPm()
                    self.resetView()
                else:
                    messageBox(
                        "New pm error",
                        "New pm can't be a pm with the same date as a pm existing with the same frequency !",
                    )
            elif self.actionToken == "Modif":
                if self.selectedpm is not None:
                    self.modifyPm()
                    self.resetView()
        else:
            messageBox(
                "Missing Information", "Please review the missing information(s)"
            )

    def showPm(self):
        self.pmdate.setDate(QDate(self.selectedpm.date))
        freq_value = self.selectedpm.freq.value
        index = self.freqcombo.findText(str(freq_value), QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.freqcombo.setCurrentIndex(index)
        self.comtext.setPlainText(self.selectedpm.com)

    def addPm(self):
        """
        Create the new PM and add it to the list of PM of the selected pump
        Check if the selected PM frequency validate other PM freqency and create and add the related PM if so.
        """
        # Create new PM and add it to pump PM
        newid = self.datas.get_new_id("pm")
        freq = self.freqmodel.getItem(self.freqcombo.currentIndex())
        date = Utility.qdate_to_str(self.pmdate.date())
        com = self.comtext.toPlainText()
        pm = PM(newid, self.pump.id, freq, date, com)
        self.model.addItem(pm)
        self.datas.pm.append(pm)

        # check for associated PM, create new PM and add it to pump PM
        selected_struct = self.pump.struct
        associateded_freqs = selected_struct.freqs_id_associated[freq.id]
        for freq_id in associateded_freqs:
            newid = self.datas.get_new_id("pm")
            com = "Generated by {} month PM".format(freq)
            freq = self.datas.freq(int(freq_id))
            pm = PM(newid, self.pump.id, freq, date, com)

            self.model.addItem(pm)
            self.datas.pm.append(pm)

        # Save the PM(s)
        self.datas.save_pm()

    def modifyPm(self):
        id = self.selectedpm.id
        date = Utility.qdate_to_str(self.pmdate.date())
        com = self.comtext.toPlainText()

        temp_pm = PM(id, self.pump.id, self.selectedpm.freq, date, com)
        for i, pm in enumerate(self.pump.pm):
            if pm.id == temp_pm.id:
                self.model.updateItem(i, temp_pm)
                break

        for i, pm in enumerate(self.datas.pm):
            if pm.id == temp_pm.id:
                self.datas.pm[i] = temp_pm
                break

        selected_struct = self.pump.struct
        associated_freqs = selected_struct.freqs_id_associated[self.selectedpm.freq.id]
        associated_pm = self.pump.get_associated_pm(self.selectedpm, associated_freqs)

        for pm_to_update in associated_pm:
            pm_to_update.date = date
            for i, pm in enumerate(self.pump.pm):
                if pm.id == pm_to_update.id:
                    self.model.updateItem(i, pm_to_update)
                    break

            for i, pm in enumerate(self.datas.pm):
                if pm.id == pm_to_update.id:
                    self.datas.pm[i] = pm_to_update
                    break

        self.datas.save_pm()

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()

    def resetView(self):
        self.selectedpm = None
        self.actionToken = ""
        self.freqcombo.setEnabled(True)
        self.dataframe.hide()
        self.selectframe.show()
