from View.BasicDialog import BasicDialog
from Model.model import messageBox, BasicListModel
from Model.objects import Type


class TypeWindow(BasicDialog):
    """Type Window"""

    def __init__(self, parent, *args, **kwargs):
        """Initializer."""
        super(TypeWindow, self).__init__(parent, *args, **kwargs)

    def initmodel(self):
        self.model = BasicListModel(self.datas.types)
        self.list.setModel(self.model)

    def deleteclicked(self):
        if len(self.list.selectionModel().selection().indexes()) > 0:
            del_index = self.list.selectionModel().selection().indexes()[0]
            temp_type = self.datas.types[del_index.row()]
            type_in_struct = temp_type.exist(
                [struct.type for struct in self.datas.struct]
            )
            if type_in_struct is None:
                type_in_pumps = temp_type.exist(
                    [pump.type for pump in self.datas.pumps]
                )
                if type_in_pumps is None:
                    self.model.removeItem(del_index.row())
                    self.datas.save_type()
                    self.selectedItem = None
                else:
                    messageBox(
                        "Type used in a pump",
                        "You can't delete a type used in a pump. Please manage the pump first !",
                    )
            else:
                messageBox(
                    "Type used in structure",
                    "You can't delete a type used in the structure. Please update the structure first !",
                )
        else:
            messageBox("Selection Error", "Please select a pump type")

    def validateclicked(self):
        if self.text.text() != "":
            temp_type = Type(0, self.text.text()).exist(self.datas.types)
            if temp_type is None or temp_type == self.selectedItem:
                if self.actionToken == "Add":
                    self.addType()
                    self.resetview()
                elif self.actionToken == "Modif":
                    if self.selectedItem is not None:
                        self.modifyType()
                        self.resetview()
            else:
                messageBox(
                    "New Type error",
                    "New pump Type can't have the same value that existing pump type !",
                )
        else:
            messageBox(
                "Missing Information", "Please review the missing information(s)"
            )

    def addType(self):
        newid = self.datas.get_new_id("types")
        type_value = self.text.text()
        type = Type(newid, type_value)
        self.model.addItem(type)
        self.datas.save_type()

    def modifyType(self):
        selected_id = self.selectedItem.id
        for i, type in enumerate(self.datas.types):
            if type.id == selected_id:
                self.datas.types[i].value = self.text.text()
                self.model.updateItem(i, self.datas.types[i])
                self.datas.save_type()
                break
