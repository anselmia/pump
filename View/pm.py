from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate, pyqtSignal
from Model.model import messageBox, PMListModel, BasicComboModel, PMStructure
from Model.objects import PM
from datetime import date

class PMWindow(QMainWindow):
    """ PM Window"""

    window_closed = pyqtSignal()

    def __init__(self, pump, parent,*args, **kwargs):
        """Initializer."""
        super(PMWindow, self).__init__(parent,*args, **kwargs)
        loadUi("UI/pm.ui", self)
        self.datas = self.parent().datas 
        self.pump = pump
        self.actionToken = ""
        self.selectedpm = None

        self.initWidgets()              

    def initWidgets(self):
        self.selectframe.show()
        self.dataframe.hide()

        self.model = PMListModel(self.pump.pm, self.datas.freqs)
        self.pmlist.setModel(self.model)
        
        actualLoc = self.pump.get_actual_loc()
 
        if actualLoc.id == "1":
            SelectedFreqs = self.datas.freqs
        else:
            SelectedFreqs = PMStructure(actualLoc, self.pump.type, []).exist(self.datas.struct).freqs

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
            self.showPm()

    def deletepmclicked(self):
        if len(self.pmlist.selectionModel().selection().indexes()) > 0:
            del_index = self.pmlist.selectionModel().selection().indexes()[0]
            self.model.removeItem(del_index.row())
            self.selectedpm = None
        else:
            messageBox("Selection Error", "Please select a pm")

    def cancelclicked(self):
        self.actionToken = ""
        self.dataframe.hide()
        self.selectframe.show()
    
    def validateclicked(self):
        if self.freqcombo.currentIndex() >= 0 :
            selected_freq = self.freqmodel.getItem(self.freqcombo.currentIndex())
            selected_struct = next((struct for struct in self.datas.struct if struct.loc == self.pump.get_actual_loc() and struct.type == self.pump.type), None)
            freq_in_struc = selected_freq.exist(selected_struct.freqs)
            if freq_in_struc is not None or self.pump.get_actual_loc().id == "1":
                if self.actionToken == "Add":
                    pm = PM(selected_freq, self.pmdate.date().toString("yyyy/MM/dd"), "")                  
                    freq_in_pm = pm.exist(self.pump.pm)
                    if freq_in_pm is None:
                        self.addPm()
                        self.dataframe.hide()
                        self.selectframe.show()
                        self.actionToken = "" 
                    else:
                        messageBox("New pm error", "New pm can't be a pm with the same date as a pm existing with the same frequency !")
                elif self.actionToken == "Modif":
                    if self.selectedpm is not None:
                        self.modifyPm() 
                        self.dataframe.hide()
                        self.selectframe.show()
                        self.actionToken = ""
            else:
                messageBox("pm frequency error", "This pump doesn't have pm at this frequency !")
        else:
            messageBox("Missing Information", "Please review the missing information(s)")    
    
    def showPm(self):
        self.pmdate.setDate(QDate(self.selectedpm.date))
        freq_value = next((freq.value for freq in self.datas.freqs if freq.id == self.selectedpm.freq.id), None)
        index = self.freqcombo.findText(freq_value, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.freqcombo.setCurrentIndex(index)
        self.comtext.setPlainText(self.selectedpm.com)

    def addPm(self):
        freq = self.freqmodel.getItem(self.freqcombo.currentIndex())
        date = self.pmdate.date().toString("yyyy/MM/dd")
        com = self.comtext.toPlainText()
        pm = PM(freq, date, com)
        self.model.addItem(pm)
        self.selectedpm = pm

    def modifyPm(self):
        selectedDate = self.selectedpm.date
        for i, pm in enumerate(self.pump.pm):
            if pm.date == selectedDate:
                self.pump.pm[i].freq = self.freqmodel.getItem(self.freqcombo.currentIndex())
                self.pump.pm[i].date = self.pmdate.date().toPyDate()
                self.pump.pm[i].com = self.comtext.toPlainText()
                self.model.updateItem(i, self.pump.pm[i])  
                self.selectedpm = self.pump.pm[i]
                break

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()