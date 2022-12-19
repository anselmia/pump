from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal
from Model.model import messageBox, PumpListModel, HistListModel, PMListModel, BasicComboModel
from Model.objects import Pump, Type
from View.history import HistWindow
from View.pm import PMWindow

class PumpWindow(QMainWindow):
    
    window_closed = pyqtSignal()

    """Main Window."""
    def __init__(self, parent,*args, **kwargs):
        """Initializer."""
        super(PumpWindow, self).__init__(parent,*args, **kwargs)
        loadUi("UI/pump_manager.ui", self)   

        self.datas = self.parent().datas   
        self.resetView()  

        self.initWidgets()        
        
    def initWidgets(self):
        self.pumpmodel = PumpListModel(self.datas.pumps, self.datas.types, self.datas.locs)
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
                    self.pmwin = PMWindow(self.selectedPump, parent=self)
                    self.pmwin.window_closed.connect(self.update_pm)
                    self.pmwin.show()
                else:
                    messageBox("Uninstalled Location", "There can be only uninstalled location to manage pm")
            else:
                messageBox("Pump type selection error", "Please select a pump type before to manage pm")
        else:
            messageBox("Missing location history", "Please add a location history before to manage pm")

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
        self.selectedPump = Pump("", "", "", [], [])

    def modifpumpclicked(self):
        if self.selectedPump is not None:
            self.selectframe.hide()
            self.dataframe.show()
            self.actionToken = "Modif"
            self.showpump()

    def deletepumpclicked(self):
        if len(self.pumplist.selectionModel().selection().indexes()) > 0:
            del_index = self.pumplist.selectionModel().selection().indexes()[0]
            self.pumpmodel.removeItem(del_index.row())
            self.datas.save_pump()
            self.selectedPump = None
        else:
            messageBox("Selection Error", "Please select a pump")

    def cancelclicked(self):
        self.resetView()  
    
    def validateclicked(self):
        if self.historymodel.rowCount() > 0 and self.typecombo.currentIndex() >= 0 and self.lineserial.text() != "":
            if self.actionToken == "Add":
                type = self.typemodel.getItem(self.typecombo.currentIndex())
                serial = self.lineserial.text()
                temp_pump = Pump("", type, serial, [], []).exist(self.datas.pumps)
                if temp_pump is None :            
                    added = self.addPump()
                    if added:
                        self.resetView()               
                else:
                    messageBox("Existing pump", "A pump with the serial {0} already exist.".format(serial))           
            elif self.actionToken == "Modif":
                if self.selectedPump is not None:
                    self.modifyPump() 
                    self.resetView()      
        else:
            messageBox("Missing Information", "Please review the missing information(s)")
    
    def onCurrentIndexChanged(self, ix):
        if self.actionToken == "Add" and self.typecombo.currentIndex() >= 0:
            type = self.typemodel.getItem(self.typecombo.currentIndex())
            self.selectedPump.type = type

    def showpump(self):        
        index = self.typecombo.findText(self.selectedPump.type.value, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.typecombo.setCurrentIndex(index)

        self.lineserial.setText(self.selectedPump.serial)

        self.historymodel = HistListModel(self.selectedPump.lochistory, self.datas.locs)
        self.loclist.setModel(self.historymodel)

        self.pmmodel = PMListModel(self.selectedPump.pm, self.datas.freqs)
        self.pmlist.setModel(self.pmmodel)

    def addPump(self):
        added = True
        if len(self.datas.pumps) > 0:
            newid = max([int(pump.id) for pump in self.datas.pumps]) + 1
        else:
            newid = 1
        
        type = self.typemodel.getItem(self.typecombo.currentIndex())
        serial = self.lineserial.text()
        pms = self.pmmodel.getAllItem()
        loc_history = self.historymodel.getAllItem()

        newpump = Pump(newid, type, serial, pms, loc_history)
        if newpump.location_free(self.datas.pumps):
            self.pumpmodel.addItem(newpump)
            self.datas.save_pump()
            self.selectedPump = newpump
        else:
            added = False
            messageBox("Location not free", "A pump of the the same type as already been installed at this location. Please select an other location or unintalled the other one first")
        
        return added
    
    def modifyPump(self):
        selectedSerial = self.selectedPump.serial
        for i, pump in enumerate(self.datas.pumps):
            if pump.serial == selectedSerial:
                self.datas.pumps[i].type = self.typemodel.getItem(self.typecombo.currentIndex())  
                self.datas.pumps[i].serial = self.lineserial.text()
                self.datas.pumps[i].lochistory = self.historymodel.getAllItem()
                self.datas.pumps[i].pm = self.pmmodel.getAllItem()
                self.pumpmodel.updateItem(i, self.datas.pumps[i])
                self.datas.save_pump()
                self.selectedPump = self.datas.pumps[i]
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

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()