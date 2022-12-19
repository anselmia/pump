from PyQt5.QtWidgets import QDialog
from PyQt5 import QtCore
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal, Qt
from Model.model import messageBox, StructListModel, RulesListModel, BasicComboModel
from Model.objects import Rules

class RulesWindow(QDialog):
    
    window_closed = pyqtSignal()

    """Rules Window."""
    def __init__(self, parent,*args, **kwargs):
        """Initializer."""
        super(RulesWindow, self).__init__(parent,*args, **kwargs)
        loadUi("UI/rules.ui", self)
    
        self.datas = self.parent().datas   
        self.resetView()

        self.initWidgets()        
        
    def initWidgets(self):
        self.dircombo.addItem('+')
        self.dircombo.addItem('-')

        self.rulesmodel = RulesListModel(self.datas.rules, self.datas.locs, self.datas.types, self.datas.freqs)
        self.ruleslist.setModel(self.rulesmodel)

        self.structfrommodel = StructListModel(self.datas.struct, self.datas.locs, self.datas.types)
        self.structfromlist.setModel(self.structfrommodel)
        
        self.structtomodel = StructListModel(self.datas.struct, self.datas.locs, self.datas.types)
        self.structtolist.setModel(self.structtomodel)

        self.freqmodel = BasicComboModel(self.datas.freqs)
        self.freqcombo.setModel(self.freqmodel)

        self.addbutton.clicked.connect(self.addClicked)
        self.modifbutton.clicked.connect(self.modifClicked)
        self.cancelbutton.clicked.connect(self.cancelclicked)
        self.validatebutton.clicked.connect(self.validateclicked)
        self.deletebutton.clicked.connect(self.deleteClicked)
        self.ruleslist.selectionModel().currentChanged.connect(self.RulesSelected)
        self.ruleslist.clicked.connect(self.RulesClicked)
        self.structfromlist.selectionModel().currentChanged.connect(self.FromSelected)
        self.structfromlist.clicked.connect(self.FromClicked)
        self.structtolist.selectionModel().currentChanged.connect(self.ToSelected)
        self.structtolist.clicked.connect(self.ToClicked)
 
    def RulesSelected(self, index):
        if len(self.ruleslist.selectionModel().selection().indexes()) > 0:
            self.selectedRule = self.rulesmodel.getItem(index)
    
    def RulesClicked(self, index):
        if len(self.ruleslist.selectionModel().selection().indexes()) > 0:
            self.selectedRule = self.rulesmodel.getItem(index)

    def FromSelected(self, index):
        if len(self.structfromlist.selectionModel().selection().indexes()) > 0:
            self.selectedStructFrom = self.structfrommodel.getItem(index)
            struct_copy = self.datas.struct.copy()
            struct_copy.remove(self.selectedStructFrom)
            self.structtomodel = StructListModel(struct_copy, self.datas.locs, self.datas.types)
            self.structtolist.setModel(self.structtomodel)

    def FromClicked(self, index):
        if len(self.structfromlist.selectionModel().selection().indexes()) > 0:
            self.selectedStructFrom = self.structfrommodel.getItem(index)
            struct_copy = self.datas.struct.copy()
            struct_copy.remove(self.selectedStructFrom)
            self.structtomodel = StructListModel(struct_copy, self.datas.locs, self.datas.types)
            self.structtolist.setModel(self.structtomodel)

    def ToSelected(self, index):
        if len(self.structtolist.selectionModel().selection().indexes()) > 0:
            self.selectedStructTo = self.structtomodel.getItem(index)
            freqs = self.selectedStructTo.freqs
            self.freqmodel = BasicComboModel(freqs)
            self.freqcombo.setModel(self.freqmodel)
    
    def ToClicked(self, index):
        if len(self.structtolist.selectionModel().selection().indexes()) > 0:
            self.selectedStructTo = self.structtomodel.getItem(index)
            freqs = self.selectedStructTo.freqs
            self.freqmodel = BasicComboModel(freqs)
            self.freqcombo.setModel(self.freqmodel)

    def addClicked(self):
        self.actionToken = "Add"
        self.selectframe.hide()
        self.dataframe.show()
        self.structfromlist.clearSelection() 
        self.structtolist.clearSelection()
        self.selectedRule = Rules("", "", "", "", "",)
        self.freqcombo.clear()  
        self.freqspin.setValue(1)
        self.dircombo.setCurrentIndex(-1)

    def modifClicked(self):
        if self.selectedRule is not None:
            self.selectframe.hide()
            self.dataframe.show()
            self.actionToken = "Modif"            
            self.showRules()
            self.structfromlist.setEnabled(False)
            self.structfromlist.setEnabled(False)
            self.structtolist.setEnabled(False)
            self.structtolist.setEnabled(False)
            self.freqcombo.setEnabled(False)

    def deleteClicked(self):
        if len(self.ruleslist.selectionModel().selection().indexes()) > 0:
            del_index = self.ruleslist.selectionModel().selection().indexes()[0]
            self.rulesmodel.removeItem(del_index.row())
            self.datas.save_rules()
            self.selectedRule = None
        else:
            messageBox("Selection Error", "Please select a rule !")

    def cancelclicked(self):
        self.resetView()
    
    def validateclicked(self):
        if self.selectedStructFrom is not None and self.selectedStructTo is not None and self.freqcombo.currentIndex() >= 0 and self.dircombo.currentIndex() >= 0:
            temp_rule = Rules(self.selectedStructFrom, self.selectedStructTo, self.freqmodel.getItem(self.freqcombo.currentIndex()), "", "").exist(self.datas.rules)
            if temp_rule is None or temp_rule == self.selectedRule: 
                if self.actionToken == "Add":                           
                    self.addRule()                    
                    self.resetView()           
            
                elif self.actionToken == "Modif":
                    if self.selectedRule is not None:
                        self.modifyRule() 
                        self.dataframe.hide()
                        self.selectframe.show()
                        self.resetView()
            else:
                messageBox("Existing rules", "A similar rules already exist.")             
        else:
            messageBox("Missing Information", "Please review the missing information(s)")

    def showRules(self):
        self.selectedStructFrom = next(struct for struct in self.datas.struct if struct == self.selectedRule.struct_from)
        index_in_rules_list = self.datas.struct.index(self.selectedStructFrom)
        qindex = self.structfrommodel.index(index_in_rules_list, 0)
        self.structfromlist.setCurrentIndex(qindex)

        self.selectedStructTo = next(struct for struct in self.datas.struct if struct == self.selectedRule.struct_to)
        index_in_rules_list = self.datas.struct.index(self.selectedStructTo)
        qindex = self.structtomodel.index(index_in_rules_list, 0)
        self.structtolist.setCurrentIndex(qindex)

        row = self.freqcombo.findText(self.selectedRule.freq.value, Qt.MatchFixedString)
        if row >= 0:
            self.freqcombo.setCurrentIndex(row)
        
        self.freqspin.setValue(int(self.selectedRule.next_pm))

        if self.selectedRule.dir == "+":
            self.dircombo.setCurrentIndex(0)
        else:
            self.dircombo.setCurrentIndex(1)

    def addRule(self):
        freq = self.freqmodel.getItem(self.freqcombo.currentIndex())
        next_pm = self.freqspin.value()
        dir = self.dircombo.currentText()
        newrule = Rules(self.selectedStructFrom, self.selectedStructTo, freq, next_pm, dir)
        self.rulesmodel.addItem(newrule)
        self.datas.save_rules()
        self.selectedRule = newrule
    
    def modifyRule(self):
        for i, rule in enumerate(self.datas.rules):
            if rule == self.selectedRule:
                self.datas.rules[i].next_pm = self.freqspin.value()
                self.datas.rules[i].dir = self.dircombo.currentText()
                self.rulesmodel.updateItem(i, self.datas.rules[i])
                self.datas.save_rules()
                self.selectedRule = self.datas.rules[i]
                break
    
    def resetView(self):
        self.selectedRule = None
        self.selectedStructFrom = None
        self.selectedStructTo = None
        self.actionToken = ""
        self.selectframe.show()
        self.dataframe.hide()
        self.freqcombo.clear()  
        self.freqspin.setValue(1)
        self.structfromlist.setEnabled(True)
        self.structfromlist.setEnabled(True)
        self.structtolist.setEnabled(True)
        self.structtolist.setEnabled(True)
        self.freqcombo.setEnabled(True)
        self.dircombo.setCurrentIndex(-1)

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()