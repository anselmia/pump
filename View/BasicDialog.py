from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi


class BasicDialog(QDialog):
    """Dialog Template Window"""

    def __init__(self, parent, ui=None, *args, **kwargs):
        """Initializer."""
        super(BasicDialog, self).__init__(parent, *args, **kwargs)
        if ui == None:
            loadUi("UI/basic_dialog.ui", self)
        else:
            loadUi(ui, self)
        self.datas = self.parent().datas
        self.selectedItem = None

        self.initWidgets()

    def initWidgets(self):
        self.initmodel()
        self.resetview()

        self.deletebutton.clicked.connect(self.deleteclicked)
        self.validatebutton.clicked.connect(self.validateclicked)
        self.addbutton.clicked.connect(self.addclicked)
        self.modifbutton.clicked.connect(self.modifclicked)
        self.cancelbutton.clicked.connect(self.cancelclicked)
        self.list.selectionModel().selectionChanged.connect(self.selected)
        self.list.clicked.connect(self.clicked)

    def selected(self, index):
        if len(self.list.selectionModel().selection().indexes()) > 0:
            self.selectedItem = self.model.getItem(index.indexes()[0])

    def clicked(self, index):
        if len(self.list.selectionModel().selection().indexes()) > 0:
            self.selectedItem = self.model.getItem(index)

    def addclicked(self):
        self.actionToken = "Add"
        self.selectframe.hide()
        self.dataframe.show()
        self.text.setText("")
        self.selectedItem = None

    def modifclicked(self):
        if self.selectedItem is not None:
            self.selectframe.hide()
            self.dataframe.show()
            self.actionToken = "Modif"
            self.showItem()

    def cancelclicked(self):
        self.resetview()

    def showItem(self):
        self.text.setText(str(self.selectedItem.value))

    def resetview(self):
        self.dataframe.hide()
        self.selectframe.show()
        self.actionToken = ""

    def closeEvent(self, event):
        self.resetview()
