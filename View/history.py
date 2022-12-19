from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate, pyqtSignal
from Model.model import messageBox, HistListModel, BasicComboModel
from Model.objects import Pump, LocHistory, PMStructure
from datetime import date, datetime

class HistWindow(QMainWindow):
    """ Localisation Window"""

    window_closed = pyqtSignal()

    def __init__(self, pump, parent,*args, **kwargs):
        """Initializer."""
        super(HistWindow, self).__init__(parent,*args, **kwargs)
        loadUi("UI/history.ui", self)
        self.datas = self.parent().datas
        self.pump = pump
        self.actionToken = ""
        self.selectedHistory = None

        self.initWidgets()        

    def initWidgets(self):
        self.selectframe.show()
        self.dataframe.hide()

        self.model = HistListModel(self.pump.lochistory, self.datas.locs)
        self.loclist.setModel(self.model)

        locs_in_struct_with_selected_pump_type = [struct.loc for struct in self.datas.struct if self.pump.type == struct.type]
        locs_in_struct_with_selected_pump_type.append(next(loc for loc in self.datas.locs if loc.id == "1"))
        self.locmodel = BasicComboModel(locs_in_struct_with_selected_pump_type)
        self.loccombo.setModel(self.locmodel)   

        self.addbutton.clicked.connect(self.addlocclicked)
        self.modifbutton.clicked.connect(self.modiflocclicked)
        self.deletebutton.clicked.connect(self.deletelocclicked)
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

    def addlocclicked(self):
        self.actionToken = "Add"
        self.selectframe.hide()
        self.dataframe.show()
        self.loccombo.setCurrentIndex(0)
        self.locdate.setDate(QDate(date.today()))

    def modiflocclicked(self):
        if self.selectedHistory is not None:
            self.selectframe.hide()
            self.dataframe.show()
            self.actionToken = "Modif"
            self.showHistory()

    def deletelocclicked(self):
        if len(self.loclist.selectionModel().selection().indexes()) > 0:
            if len(self.model.items) > 1:
                del_index = self.loclist.selectionModel().selection().indexes()[0]
                self.model.removeItem(del_index.row())
                self.selectedHistory = None
            else:
                messageBox("Deletion Error", "There must be at least one location history")
        else:
            messageBox("Selection Error", "Please select a location history")

    def cancelclicked(self):
        self.actionToken = ""
        self.dataframe.hide()
        self.selectframe.show()
    
    def validateclicked(self):  
        if self.loccombo.currentIndex() >= 0 : 
            selected_loc = self.locmodel.getItem(self.loccombo.currentIndex())
            temp_struct = PMStructure(
                selected_loc,
                self.pump.type,
                []                
            )
            pump_in_struct = temp_struct.exist(self.datas.struct)
            if pump_in_struct is not None or selected_loc.id == "1":            
                if self.actionToken == "Add":
                    temp_hist = LocHistory(selected_loc, self.locdate.date().toString("yyyy/MM/dd"))   
                    hist_in_pump = temp_hist.exist(self.pump.lochistory)
                    if hist_in_pump is None:
                        lastloc = self.pump.get_actual_loc()
                        newloc = next((loc for loc in self.datas.locs if loc.value == self.loccombo.currentText()), None)           
                        if lastloc is None or lastloc != newloc :
                            self.addHistory()

                            self.dataframe.hide()
                            self.selectframe.show()
                            self.actionToken = ""
                        else:
                            messageBox("New location error", "New location must be different from previous loc !")
                    else:
                        messageBox("Existing History", "A pump has already been installed at this date.")
                elif self.actionToken == "Modif":
                    if self.selectedHistory is not None:
                        self.modifyHistory() 
                        self.dataframe.hide()
                        self.selectframe.show()
                        self.actionToken = "" 
            else:
                messageBox("Structure error", "This pump is not in the structure !")  
        else:
            messageBox("Missing Information", "Please review the missing information(s)")    
        
    def showHistory(self):        
        self.locdate.setDate(QDate(self.selectedHistory.date))
        loc_value = self.selectedHistory.loc.value   
        index = self.loccombo.findText(loc_value, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.loccombo.setCurrentIndex(index)

    def addHistory(self):
        loc = self.locmodel.getItem(self.loccombo.currentIndex())
        date = self.locdate.date().toString("yyyy/MM/dd")
        lochistory = LocHistory(loc, date)
        self.model.addItem(lochistory)
        self.selectedHistory = lochistory

    def modifyHistory(self):
        selectedDate = self.selectedHistory.date
        for i, lochistory in enumerate(self.pump.lochistory):
            if lochistory.date == selectedDate:
                self.pump.lochistory[i].loc = self.locmodel.getItem(self.loccombo.currentIndex())
                self.pump.lochistory[i].date = datetime.strptime(self.locdate.date().toString("yyyy/MM/dd"), "%Y/%m/%d")
                self.model.updateItem(i, self.pump.lochistory[i])  
                self.selectedHistory = self.pump.lochistory[i]
                break

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()