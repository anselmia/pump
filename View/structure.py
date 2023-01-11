from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import QtCore
from View.BasicDialog import BasicDialog
from Model.model import messageBox, StructListModel, BasicComboModel, FreqListModel
from Model.objects import Structure


class StructWindow(BasicDialog):
    """PM Window"""

    window_closed = pyqtSignal()

    def __init__(self, parent, *args, **kwargs):
        """Initializer."""
        super(StructWindow, self).__init__(parent, "UI/structure.ui", *args, **kwargs)
        self.initAdditionalWidgets()

    def initmodel(self):
        self.model = StructListModel(
            self.datas.struct, self.datas.locs, self.datas.types
        )
        self.list.setModel(self.model)

        self.locmodel = BasicComboModel(self.datas.locs)
        self.loccombo.setModel(self.locmodel)

        self.typemodel = BasicComboModel(self.datas.types)
        self.typecombo.setModel(self.typemodel)

        self.freqmodel = FreqListModel([])
        self.freqlist.setModel(self.freqmodel)

        self.freqmodel2 = FreqListModel(self.datas.freqs)
        self.freqlist2.setModel(self.freqmodel2)

        self.attfreqmodel = FreqListModel([])
        self.attfreqlist.setModel(self.attfreqmodel)

        self.attfreqmodel2 = FreqListModel([])
        self.attfreqlist2.setModel(self.attfreqmodel2)

    def initAdditionalWidgets(self):
        self.addfreqbutton.clicked.connect(self.addFreq)
        self.removefreqbutton.clicked.connect(self.removeFreq)
        self.addattfreqbutton.clicked.connect(self.addAttFreq)
        self.removeattfreqbutton.clicked.connect(self.removeAttFreq)
        self.freqlist.selectionModel().selectionChanged.connect(self.freqselected)
        self.freqlist.clicked.connect(self.freqclicked)

    def freqselected(self, index):
        if len(index.indexes()) > 0:
            self.selectedFreq = self.freqmodel.getItem(index.indexes()[0])
            associatedfreqid = self.selectedItem.temp_freqs_id_associated[
                self.selectedFreq.id
            ]
            associatedfreq = []
            for id in associatedfreqid:
                associatedfreq.append(
                    next(freq for freq in self.datas.freqs if freq.id == id)
                )
            self.attfreqmodel = FreqListModel(associatedfreq)
            self.attfreqlist.setModel(self.attfreqmodel)
            associatedfreq2 = self.freqmodel.items.copy()
            selected_freq = next(
                freq for freq in associatedfreq2 if freq.id == self.selectedFreq.id
            )
            associatedfreq2.remove(selected_freq)
            for freq in self.attfreqmodel.items:
                freq = next(_freq for _freq in associatedfreq2 if freq.id == _freq.id)
                associatedfreq2.remove(freq)
            self.attfreqmodel2 = FreqListModel(associatedfreq2)
            self.attfreqlist2.setModel(self.attfreqmodel2)

    def freqclicked(self, index):
        if len(self.freqlist.selectionModel().selection().indexes()) > 0:
            self.selectedFreq = self.freqmodel.getItem(index)
            associatedfreqid = self.selectedItem.temp_freqs_id_associated[
                self.selectedFreq.id
            ]
            associatedfreq = []
            for id in associatedfreqid:
                associatedfreq.append(
                    next(freq for freq in self.datas.freqs if freq.id == id)
                )
            self.attfreqmodel = FreqListModel(associatedfreq)
            self.attfreqlist.setModel(self.attfreqmodel)
            associatedfreq2 = self.freqmodel.items.copy()
            selected_freq = next(
                freq for freq in associatedfreq2 if freq.id == self.selectedFreq.id
            )
            associatedfreq2.remove(selected_freq)
            for freq in self.attfreqmodel.items:
                freq = next(_freq for _freq in associatedfreq2 if freq.id == _freq.id)
                associatedfreq2.remove(freq)
            self.attfreqmodel2 = FreqListModel(associatedfreq2)
            self.attfreqlist2.setModel(self.attfreqmodel2)

    def addFreq(self):
        if len(self.freqlist2.selectionModel().selection().indexes()) > 0:
            selectedFreq = self.freqmodel2.getItem(
                self.freqlist2.selectionModel().selection().indexes()[0]
            )
            if not selectedFreq in self.freqmodel.items:
                self.freqmodel.addItem(selectedFreq)
                self.selectedItem.temp_freqs_id_associated[selectedFreq.id] = []

    def removeFreq(self):
        if len(self.freqlist.selectionModel().selection().indexes()) > 0:
            id = self.freqmodel.getItem(
                self.freqlist.selectionModel().selection().indexes()[0]
            ).id
            self.freqmodel.removeItem(
                self.freqlist.selectionModel().selection().indexes()[0].row()
            )
            self.selectedItem.temp_freqs_id_associated.pop(id)

    def addAttFreq(self):
        if len(self.attfreqlist2.selectionModel().selection().indexes()) > 0:
            selectedFreq = self.attfreqmodel2.getItem(
                self.attfreqlist2.selectionModel().selection().indexes()[0]
            )
            if not selectedFreq in self.attfreqmodel.items:
                self.attfreqmodel.addItem(selectedFreq)
                self.selectedItem.temp_freqs_id_associated[self.selectedFreq.id].append(
                    selectedFreq.id
                )
                index = self.attfreqmodel2.find_index_from_text(
                    "{0} month".format(selectedFreq.value)
                )

                if index >= 0:
                    self.attfreqmodel2.removeItem(index)

    def removeAttFreq(self):
        if len(self.attfreqlist.selectionModel().selection().indexes()) > 0:
            selectedAttFreq = self.attfreqmodel.getItem(
                self.attfreqlist.selectionModel().selection().indexes()[0]
            )
            self.attfreqmodel.removeItem(
                self.attfreqlist.selectionModel().selection().indexes()[0].row()
            )
            self.selectedItem.temp_freqs_id_associated[self.selectedFreq.id].remove(
                selectedAttFreq.id
            )
            self.attfreqmodel2.addItem(selectedAttFreq)

    def addclicked(self):
        self.actionToken = "Add"
        self.selectframe.hide()
        self.dataframe.show()
        self.typecombo.setCurrentIndex(-1)
        self.loccombo.setCurrentIndex(-1)
        self.freqmodel.clear()
        self.selectedItem = Structure("", "", [], [])

    def modifclicked(self):
        if self.selectedItem is not None:
            self.selectframe.hide()
            self.dataframe.show()
            self.actionToken = "Modif"
            self.selectedItem.temp_freqs = self.selectedItem.freqs.copy()
            self.selectedItem.temp_freqs_id_associated = (
                self.selectedItem.freqs_id_associated.copy()
            )
            self.showItem()

    def showItem(self):
        location = self.selectedItem.loc
        row = self.loccombo.findText(location.value, Qt.MatchFixedString)
        if row >= 0:
            self.loccombo.setCurrentIndex(row)

        type = self.selectedItem.type
        row = self.typecombo.findText(type.value, Qt.MatchFixedString)
        if row >= 0:
            self.typecombo.setCurrentIndex(row)

        self.freqmodel = FreqListModel(self.selectedItem.temp_freqs)
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
        if (
            len(self.freqmodel.items) > 0
            and self.loccombo.currentIndex() >= 0
            and self.typecombo.currentIndex() >= 0
        ):
            loc = self.locmodel.getItem(self.loccombo.currentIndex())
            type = self.typemodel.getItem(self.typecombo.currentIndex())
            temp_struct = Structure(loc, type, [], []).exist(self.datas.struct)
            if temp_struct is None or temp_struct == self.selectedItem:

                if self.actionToken == "Add":
                    self.addStruct()
                    self.resetview()
                elif self.actionToken == "Modif":
                    self.modifyStruct()
                    self.resetview()
            else:
                messageBox(
                    "New structure error",
                    "A structure with the same location and type already exist !",
                )
        else:
            messageBox(
                "Missing Information", "Please review the missing information(s)"
            )

    def addStruct(self):
        type = self.typemodel.getItem(self.typecombo.currentIndex())
        loc = self.locmodel.getItem(self.loccombo.currentIndex())

        newstruct = Structure(
            loc,
            type,
            self.selectedItem.temp_freqs,
            self.selectedItem.temp_freqs_id_associated,
        )
        self.model.addItem(newstruct)
        self.datas.save_structure()

    def modifyStruct(self):
        selected_loc = self.selectedItem.loc
        selected_type = self.selectedItem.type
        for i, struc in enumerate(self.datas.struct):
            if struc.loc == selected_loc and struc.type == selected_type:
                self.datas.struct[i].loc = selected_loc
                self.datas.struct[i].type = selected_type
                self.datas.struct[i].freqs = self.selectedItem.temp_freqs
                self.datas.struct[
                    i
                ].freqs_id_associated = self.selectedItem.temp_freqs_id_associated
                self.model.updateItem(i, self.datas.struct[i])
                self.datas.save_structure()
                break

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()
