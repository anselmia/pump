from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore, QtGui
from PyQt5.uic import loadUi
from model import ListPumpModel, messageBox, Pump
from datetime import date, datetime

class PumpWindow(QMainWindow):
    """Main Window."""
    def __init__(self, mainWin, parent=None):
        """Initializer."""
        super(PumpWindow, self).__init__(parent)
        loadUi("pump_manager.ui", self)
        self.datas = mainWin.datas
        self.actionToken = ""

        self.initWidgets()        
        self.show()

    def initWidgets(self):
        self.entry = QtGui.QStandardItemModel()
        self.loclabel.hide()
        self.loclist.hide()
        self.removelocbutton.hide()
        self.pmlabel.hide()
        self.pmlist.hide()
        self.cancelbutton.hide()
        self.addbutton.clicked.connect(self.addpumpclicked)
        self.cancelbutton.clicked.connect(self.cancelclicked)
        self.validatebutton.clicked.connect(self.validateclicked)
        self.deletebutton.clicked.connect(self.deletepumpclicked)
        self.listmodel = ListPumpModel(self.datas.pumps, self.datas.types)
        self.pumplist.setModel(self.listmodel)
        self.pumplist.selectionModel().currentChanged.connect(self.pumpselected)

        locs_options = [locs for index, locs in self.datas.locs.items()]
        locs_options.insert(0,"")
        for t in locs_options:
            self.comboloc.addItem(t)
        
        types_options = [types for index, types in self.datas.types.items()]
        types_options.insert(0,"")
        for t in types_options:
            self.combotype.addItem(t)

    def pumpselected(self, index):
        if index.data() != None:
            self.showpump(index)        
        else:
            self.deletebutton.setEnabled(False)
            self.validatebutton.setEnabled(False)
            self.comboloc.setCurrentIndex(0)
            self.combotype.setCurrentIndex(0)
            self.lineserial.setText("")

    def addpumpclicked(self):
        self.actionToken = "Add"
        self.loclabel.hide()
        self.loclist.hide()
        self.removelocbutton.hide()
        self.pmlabel.hide()
        self.pmlist.hide()
        self.comboloc.setCurrentIndex(0)
        self.combotype.setCurrentIndex(0)
        self.lineserial.setText("")
        self.validatebutton.setEnabled(True)
        self.cancelbutton.show()

    def deletepumpclicked(self):
        return

    def cancelclicked(self):
        self.actionToken = "Modify"
        self.loclabel.show()
        self.loclist.show()
        self.removelocbutton.show()
        self.pmlabel.show()
        self.pmlist.show()
        self.comboloc.setCurrentIndex(0)
        self.combotype.setCurrentIndex(0)
        self.lineserial.setText("")
        self.validatebutton.setEnabled(True)
        self.cancelbutton.hide()
    
    def validateclicked(self):
        if self.actionToken == "Add":
            serial = None
            for pump in self.datas.pumps:
                if pump.serial.lower() == self.lineserial.text().lower():
                    serial = pump.serial
            if serial == None:
                if self.comboloc.currentIndex() > 0 and self.combotype.currentIndex() > 0 and self.lineserial.text() != "":
                    newpump = self.addPump()

                    self.listmodel.pumps.append(newpump)
                    self.listmodel.layoutChanged.emit()

                    ix = self.entry.index(0, 0)
                    sm = self.pumplist.selectionModel()
                    sm.select(ix, QtCore.QItemSelectionModel.Select)
                    self.validatebutton.setEnabled(False)
                    self.cancelbutton.hide()     
                else:
                    messageBox("Missing Information", "Please review the missing information(s)")
            else:
                messageBox("Existing pump", "A pump with the serial " + serial + " already exist.")
                
        elif self.actionToken == "Modify":
            serial = self.modify()       
        
    def showpump(self, listindex):
        self.actionToken = "Modify"
        self.loclabel.show()
        self.loclist.show()
        self.removelocbutton.show()
        self.pmlabel.show()
        self.pmlist.show()
        serial = listindex.data().split(" ")[1]
        pump = next(pump for pump in self.datas.pumps if pump.serial == serial)            

        index = self.comboloc.findText(self.datas.locs[str(pump.localisation)], QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.comboloc.setCurrentIndex(index)
        
        index = self.combotype.findText(self.datas.types[str(pump.type)], QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.combotype.setCurrentIndex(index)

        self.lineserial.setText(pump.serial)

        self.deletebutton.setEnabled(True)
        self.validatebutton.setEnabled(True)

    def addPump(self):
        if len(self.pumps) > 0:
            newid = max([int(pump.id) for pump in self.pumps]) + 1
        else:
            newid = 1
        locindex = list(self.datas.locs.keys())[list(self.datas.locs.values()).index(self.comboloc.currentText())]
        typeindex = list(self.datas.types.keys())[list(self.datas.types.values()).index(self.combotype.currentText())]
        serial = self.lineserial.text()
        if int(locindex) > 1:
            lochistory = [str(date.today), locindex]
        else:
            lochistory = []

        newpump = Pump(newid,locindex, typeindex, serial, [], lochistory)
        self.datas.pumps.append(newpump)

        return newpump

    def modifyPump(self, pump):
        locindex = list(self.datas.locs.keys())[list(self.datas.locs.values()).index(self.comboloc.currentText())]
        pump.loc = locindex
        pump.type = list(self.datas.types.keys())[list(self.datas.types.values()).index(self.combotype.currentText())]
        pump.serial = self.lineserial.text()
        lastlocdate = str(max([datetime.strptime(loc[0], '%Y/%m/%d').date() for loc in pump.lochistory]))
        lastloc = list(pump.lochistory.keys())[list(pump.lochistory.values()).index(lastlocdate)]

        if lastloc != locindex:
            pump.lochistory[str(datetime.today.strftime('%Y/%m/%d'))] = locindex
