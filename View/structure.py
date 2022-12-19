from PyQt5.QtCore import pyqtSignal, Qt
from View.BasicDialog import BasicDialog
from Model.model import messageBox, StructListModel, BasicComboModel, FreqListModel
from Model.objects import PMStructure, Location, Type


class StructWindow(BasicDialog):
    """ PM Window"""

    window_closed = pyqtSignal()

    def __init__(self, parent,*args, **kwargs):
        """Initializer."""
        super(StructWindow, self).__init__(parent, "UI/structure.ui", *args, **kwargs)   
        self.initAdditionalWidgets()

    def initmodel(self):        
        self.model = StructListModel(self.datas.struct, self.datas.locs, self.datas.types)
        self.list.setModel(self.model)

        self.locmodel = BasicComboModel(self.datas.locs)
        self.loccombo.setModel(self.locmodel)

        self.typemodel = BasicComboModel(self.datas.types)
        self.typecombo.setModel(self.typemodel)

        self.freqmodel = FreqListModel([])
        self.freqlist.setModel(self.freqmodel)

        self.freqmodel2 = FreqListModel(self.datas.freqs)
        self.freqlist2.setModel(self.freqmodel2)

    def initAdditionalWidgets(self):
        self.addfreqbutton.clicked.connect(self.addFreq)
        self.removefreqbutton.clicked.connect(self.removeFreq)

    def addFreq(self):
        if len(self.freqlist2.selectionModel().selection().indexes()) > 0: 
            selectedFreq = self.freqmodel2.getItem(self.freqlist2.selectionModel().selection().indexes()[0])
            if not selectedFreq in self.freqmodel.items:
                self.freqmodel.addItem(selectedFreq)
    
    def removeFreq(self):
        if len(self.freqlist.selectionModel().selection().indexes()) > 0: 
            self.freqmodel.removeItem(self.freqlist.selectionModel().selection().indexes()[0].row())

    def addclicked(self):
        self.actionToken = "Add"
        self.selectframe.hide()
        self.dataframe.show()
        self.typecombo.setCurrentIndex(-1)
        self.loccombo.setCurrentIndex(-1)
        self.freqmodel.clear()
        self.selectedItem = PMStructure("", "", [])

    def showItem(self):
        location = self.selectedItem.loc
        row = self.loccombo.findText(location.value, Qt.MatchFixedString)
        if row >= 0:
            self.loccombo.setCurrentIndex(row)

        type = self.selectedItem.type
        row = self.typecombo.findText(type.value, Qt.MatchFixedString)
        if row >= 0:
            self.typecombo.setCurrentIndex(row)

        self.freqmodel = FreqListModel(self.selectedItem.freqs, self.datas.locs)
        self.freqlist.setModel(self.freqmodel)

    def deleteclicked(self):
        if len(self.list.selectionModel().selection().indexes()) > 0:
            del_index = self.list.selectionModel().selection().indexes()[0]
            self.model.removeItem(del_index.row())
            self.datas.save_structure()
            self.selectedItem = None
        else:
            messageBox("Selection Error", "Please select a structure")

    def validateclicked(self):
        if len(self.freqmodel.items) > 0 and self.loccombo.currentIndex() >= 0 and self.typecombo.currentIndex() >= 0:      
            loc = self.locmodel.getItem(self.loccombo.currentIndex())
            type = self.typemodel.getItem(self.typecombo.currentIndex())
            temp_struct = PMStructure(loc, type, []).exist(self.datas.struct)
            if temp_struct is None or temp_struct == self.selectedItem:
                if self.actionToken == "Add":                              
                        self.addStruct()
                        self.resetview()                 
                elif self.actionToken == "Modif":
                    if self.selectedItem is not None:
                            self.modifyStruct() 
                            self.resetview() 
            else:
                messageBox("New structure error", "A structure with the same location and type already exist !")
        else:
            messageBox("Missing Information", "Please review the missing information(s)")    

    def addStruct(self):        
        type = self.typemodel.getItem(self.typecombo.currentIndex())
        loc = self.locmodel.getItem(self.loccombo.currentIndex())
        freqs = self.freqmodel.getAllItem()

        newstruct = PMStructure(loc, type, freqs)
        self.model.addItem(newstruct)
        self.datas.save_structure()
        self.selectedItem = newstruct

    def modifyStruct(self):
        selected_loc = self.selectedItem.loc
        selected_type = self.selectedItem.type
        for i, struc in enumerate(self.datas.struct):
            if struc.loc == selected_loc and struc.type == selected_type:
                self.datas.struct[i].loc = selected_loc
                self.datas.struct[i].type = selected_type
                self.datas.struct[i].freqs = self.freqmodel.getAllItem()
                self.model.updateItem(i, self.datas.struct[i])  
                self.datas.save_structure()
                self.selecteditem = self.datas.struct[i]
                break
    
    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()