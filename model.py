from datetime import datetime
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
import json
import pandas as pd

class Pump: 

    def __init__(self, id, loc, type, serial, pms, lochistory):
        """
        init expect : pump type, 
        """
        self.id = id
        self.localisation = loc
        self.type = type
        self.serial = serial
        self.pm = []
        for pm in pms:
            self.pm.append(PM(pm))
        self.lochistory = lochistory

    def __str__(self):
        return self.type + " " + self.serial
    
class PM: 

    def __init__(self, pm):
        """
        init expect : pump type, 
        """
        self.frequency_id = int(pm["freq_id"])
        self.date = datetime.strptime(pm["date"], '%m/%Y')
        self.com = pm["com"]

class ListPumpModel(QtCore.QAbstractListModel):
    def __init__(self, pumps, types, *args, **kwargs, ):
        super(ListPumpModel, self).__init__(*args, **kwargs)
        self.pumps = pumps
        self.types = types

    def data(self, index, role):
        print(type(index))
        if role == Qt.DisplayRole:
            #serial = index.data().split(" ")[1]
            pump = next(pump for pump in self.datas.pumps if pump.serial == 0)            
            return self.types[str(pump.type)] + " " + pump.serial

    def rowCount(self, index):
        return len(self.pumps)

class TablePumpModel(QtCore.QAbstractTableModel):
    def __init__(self, datas):
        super(TablePumpModel, self).__init__()
        self.datas = datas
        self.init_table_data()

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self.tabledata.iloc[index.row()][index.column()]

    def rowCount(self, index):
            return self.tabledata.shape[0]

    def columnCount(self, index):
        return self.tabledata.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.tabledata.columns[section])

            if orientation == Qt.Vertical:
                return str(self.tabledata.index[section])

    def init_table_data(self):
        headerH = []
        headerV = []
        self.temp_struct = []
        self.temp_table_data = []
        for loc_id, types_id in self.datas.struct.items():            
            for type_id in types_id:
                self.temp_struct.append(type_id)
                headerH.append(self.datas.locs[loc_id] + " " + self.datas.types[type_id[0]]) 
        self.temp_table_data.append(self.temp_struct)
        self.temp_table_data.append(self.temp_struct)
        self.temp_table_data.append(self.temp_struct)
        self.temp_table_data.append(self.temp_struct)
        self.temp_table_data.append(self.temp_struct)
        
        for id,frequency in self.datas.freqs.items():
            headerV.append(str(frequency) + " month")

        self.tabledata = pd.DataFrame(
            self.temp_table_data,
            columns = headerH,
            index = headerV
        )

class Data:

    def __init__(self):
        datas = self.load_data()
        self.freqs = datas["frequency"]
        self.locs = datas["localisation"]
        self.types = datas["type"]
        self.struct = datas["structure"]
        self.pumps = []
        for pump in datas["pumps"]:
            self.pumps.append(Pump(pump["id"],pump["localisation"],pump["type"],pump["serial"],pump["pm"],pump["lochistory"]))

    def load_data(self):
        with open('datas.json', 'r') as openfile:
            # Reading from json file
            return json.load(openfile)
    
    def save_datas(datas):
        # Serializing json
        json_object = json.dumps(datas, indent=4)
        
        # Writing to sample.json
        with open("datas.json", "w") as outfile:
            outfile.write(json_object)

def messageBox(title, message):
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(QMessageBox.Critical)
    x = msg.exec_()