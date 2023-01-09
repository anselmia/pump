from PyQt5.QtWidgets import QDialog
from PyQt5 import QtCore
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal, QDate
from Model.model import messageBox, PumpComboModel, RulesListModel, BasicComboModel
from Model.objects import Rules, Utility
from datetime import date


class RulesWindow(QDialog):

    window_closed = pyqtSignal()

    """Rules Window."""

    def __init__(self, parent, *args, **kwargs):
        """Initializer."""
        super(RulesWindow, self).__init__(parent, *args, **kwargs)
        loadUi("UI/rules_type1.ui", self)

        self.datas = self.parent().datas
        self.resetView()

        self.initWidgets()

    def initWidgets(self):

        self.rulesmodel = RulesListModel(
            self.datas.rules,
            self.datas.pumps,
            self.datas.freqs,
        )
        self.list.setModel(self.rulesmodel)

        self.freqmodel = BasicComboModel(self.datas.freqs)
        self.combo.setModel(self.freqmodel)
        self.combo.setCurrentIndex(-1)

        self.pumpmodel = PumpComboModel(
            [
                pump
                for pump in self.datas.pumps
                if pump.get_last_installed_hist() is not None
            ]
        )
        self.pumpcombo.setModel(self.pumpmodel)
        self.pumpcombo.setCurrentIndex(-1)

        self.addbutton.clicked.connect(self.addClicked)
        self.modifbutton.clicked.connect(self.modifClicked)
        self.cancelbutton.clicked.connect(self.cancelclicked)
        self.validatebutton.clicked.connect(self.validateclicked)
        self.deletebutton.clicked.connect(self.deleteClicked)
        self.list.selectionModel().currentChanged.connect(self.RulesSelected)
        self.list.clicked.connect(self.RulesClicked)
        self.pumpcombo.currentIndexChanged.connect(self.pumpChanged)

    def RulesSelected(self, index):
        if len(self.list.selectionModel().selection().indexes()) > 0:
            self.selectedRule = self.rulesmodel.getItem(index)

    def RulesClicked(self, index):
        if len(self.list.selectionModel().selection().indexes()) > 0:
            self.selectedRule = self.rulesmodel.getItem(index)

    def pumpChanged(self, row):
        if self.pumpcombo.currentIndex() >= 0:
            self.selectedPump = self.pumpmodel.getItem(row)

            type = self.selectedPump.type
            loc = self.selectedPump.get_last_installed_hist().loc
            struct = next(
                struct
                for struct in self.datas.struct
                if type == struct.type and loc == struct.loc
            )
            freqs = struct.freqs

            self.freqmodel = BasicComboModel(freqs)
            self.combo.setModel(self.freqmodel)

    def addClicked(self):
        self.actionToken = "Add"
        self.selectframe.hide()
        self.dataframe.show()
        self.selectedRule = Rules(0, 0, 0, "1900/01/01", False)
        self.combo.clear()
        self.date.setDate(QDate(date.today()))
        self.pumpcombo.setCurrentIndex(-1)
        self.check.setChecked(True)

    def modifClicked(self):
        if self.selectedRule is not None:
            self.selectframe.hide()
            self.dataframe.show()
            self.actionToken = "Modif"
            self.showRules()

    def deleteClicked(self):
        if len(self.list.selectionModel().selection().indexes()) > 0:
            del_index = self.list.selectionModel().selection().indexes()[0]
            self.rulesmodel.removeItem(del_index.row())
            self.datas.save_rules()
            self.selectedRule = None
        else:
            messageBox("Selection Error", "Please select a rule !")

    def cancelclicked(self):
        self.resetView()

    def validateclicked(self):
        if self.selectedPump is not None and self.combo.currentIndex() >= 0:
            self.selectedRule.pump = self.selectedPump
            self.selectedRule.freq = self.freqmodel.getItem(self.combo.currentIndex())
            rule_to_add = Rules(
                0,
                self.selectedPump,
                self.freqmodel.getItem(self.combo.currentIndex()),
                Utility.qdate_to_str(self.date.date()),
                False,
            )
            active_rule = self.selectedPump.get_active_rule(
                rule_to_add.freq, self.datas.rules
            )

            if (
                active_rule is None or rule_to_add.date > active_rule.date
            ) or active_rule == self.selectedRule:

                if self.actionToken == "Add":
                    self.addRule()
                    self.resetView()

                elif self.actionToken == "Modif":
                    if self.selectedRule is not None:
                        self.modifyRule()
                        self.resetView()
            else:
                messageBox("Existing rules", "A similar rules already exist.")
        else:
            messageBox(
                "Missing Information", "Please review the missing information(s)"
            )

    def showRules(self):
        self.selectedPump = next(
            pump for pump in self.datas.pumps if pump == self.selectedRule.pump
        )
        combo_text = "{0} {1}".format(
            self.selectedPump.type.value, self.selectedPump.serial
        )
        index = self.pumpcombo.findText(combo_text, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.pumpcombo.setCurrentIndex(index)

        freq_value = next(
            freq.value for freq in self.datas.freqs if self.selectedRule.freq == freq
        )
        index = self.combo.findText(str(freq_value), QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.combo.setCurrentIndex(index)

        self.date.setDate(QDate(self.selectedRule.date))
        self.check.setChecked(self.selectedRule.synchro)

    def addRule(self):
        id = self.datas.get_new_id("rules")
        freq = self.freqmodel.getItem(self.combo.currentIndex())
        date = Utility.qdate_to_str(self.date.date())
        synchro = self.check.isChecked()
        newrule = Rules(id, self.selectedPump, freq, date, synchro)
        self.rulesmodel.addItem(newrule)
        self.datas.save_rules()

    def modifyRule(self):
        id = self.selectedRule.id
        pump = self.selectedRule.pump
        freq = self.freqmodel.getItem(self.combo.currentIndex())
        date = Utility.qdate_to_str(self.date.date())
        synchro = self.check.isChecked()
        temp_rule = Rules(id, pump, freq, date, synchro)
        for i, rule in enumerate(self.datas.rules):
            if rule.id == self.selectedRule.id:
                self.datas.rules[i] = temp_rule
                self.rulesmodel.updateItem(i, temp_rule)
                self.datas.save_rules()
                break

    def resetView(self):
        self.selectedRule = None
        self.selectedPump = None
        self.actionToken = ""
        self.selectframe.show()
        self.dataframe.hide()
        self.combo.clear()
        self.pumpcombo.setCurrentIndex(-1)
        self.check.setChecked(True)

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()
