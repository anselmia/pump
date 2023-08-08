from View.BasicDialog import BasicDialog
from Model.model import messageBox, BasicListModel
from Model.objects import Location

class LocWindow(BasicDialog):
    """ Location Window"""

    def __init__(self, parent,*args, **kwargs):
        """Initializer."""
        super(LocWindow, self).__init__(parent, *args, **kwargs) 

    def initmodel(self):
        self.model = BasicListModel(self.datas.locs)
        self.list.setModel(self.model)
  
    def deleteclicked(self):
        if len(self.list.selectionModel().selection().indexes()) > 0:
            del_index = self.list.selectionModel().selection().indexes()[0]
            temp_loc = self.datas.locs[del_index.row()]
            if temp_loc.id != '1':
                loc_in_struct = temp_loc.exist([struct.loc for struct in self.datas.struct])
                if loc_in_struct is None:
                    hist_locs = []
                    for pump in self.datas.pumps:
                        hist_locs.extend([hist.loc for hist in pump.lochistory]) 
                    loc_in_hist = temp_loc.exist(hist_locs)
                    if loc_in_hist is None:
                        self.model.removeItem(del_index.row())
                        self.datas.save_location()
                        self.selectedItem = None
                    else:
                        messageBox("Location used in location history", "You can't delete a location used in a location history. Please manage the location history first !")
                else:
                    messageBox("Location used in structure", "You can't delete a location used in the structure. Please update the structure first !")
            else:
                    messageBox("Uninstalled Location ", "You can't delete this location !")
        else:
            messageBox("Selection Error", "Please select a location")
    
    def validateclicked(self):
        if self.text.text() != "":
            temp_location = Location(0, self.text.text()).exist(self.datas.locs)                 
            if temp_location is None or temp_location == self.selectedItem:
                if self.actionToken == "Add":                               
                    self.addLoc()
                    self.resetview()                   
                elif self.actionToken == "Modif":
                    if self.selectedItem is not None:
                        self.modifyLoc() 
                        self.resetview()   
            else:
                messageBox("New location error", "New location can't have the same value that existing location !")                    
        else:
            messageBox("Missing Information", "Please review the missing information(s)")    
    
    def addLoc(self):
        newid = self.datas.get_new_id("locs")
        location_value = self.text.text()
        loc = Location(newid, location_value)
        self.model.addItem(loc)
        self.datas.save_location()

    def modifyLoc(self):
        selected_id = self.selectedItem.id
        for i, loc in enumerate(self.datas.locs):
            if loc.id == selected_id:
                self.datas.locs[i].value = self.text.text()
                self.model.updateItem(i, self.datas.locs[i])  
                self.datas.save_location()
                break