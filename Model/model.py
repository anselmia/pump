from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from PyQt5 import QtCore,QtGui
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from Model.objects import Rules, PMStructure
import pandas as pd

class BasicListModel(QtCore.QAbstractListModel):

    def __init__(self, items, *args, **kwargs):
        super(BasicListModel, self).__init__()
        self.items = items
        self.sort()

    def addItem(self, item):
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
        self.items.append(item)
        self.endInsertRows()
        self.sort()

    def clear(self):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount() - 1)
        self.items = []
        self.endRemoveRows()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row].value
            return "{0}".format(item)

    def getItem(self, index):
        row = index.row()
        if 0 <= row < self.rowCount():
            return self.items[row]
    
    def getAllItem(self):        
        return self.items

    def insertItem(self, item, index):
        self.beginInsertRows(QtCore.QModelIndex(), index, index)
        self.items.insert(index, item)
        self.endInsertRows()
        self.sort()

    def removeItem(self, row):
        self.beginRemoveRows(QtCore.QModelIndex(), row, row)
        del self.items[row]
        self.endRemoveRows()

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.items)

    def setData(self, index, item, role=QtCore.Qt.EditRole):
        self.items[index] = item

    def updateItem(self, index, item):
        self.setData(index, item)
        self.sort()

    def sort(self):
        self.items.sort(key=lambda x: x.value, reverse=False)
        self.layoutChanged.emit()

class FreqListModel(BasicListModel):

    def __init__(self, items, *args, **kwargs):
        super(FreqListModel, self).__init__(items)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            freq_value = self.items[row].value
            return "{0} month".format(freq_value)
    
    def sort(self):
        self.items.sort(key=lambda x: int(x.value), reverse=False)
        self.layoutChanged.emit()

class PumpListModel(BasicListModel):

    def __init__(self, items, types, locs, *args, **kwargs):
        self.types = types
        self.locs = locs

        super(PumpListModel, self).__init__(items)
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            serial = self.items[row].serial
            type_value = self.items[row].type.value
            loc_value = self.items[row].get_actual_loc().value            

            return "{0} {1} {2}".format(loc_value, type_value, serial)

    def sort(self):
        self.items.sort(key=lambda x: (next(loc for loc in self.locs if loc == x.get_actual_loc()), x.type), reverse=False)
        self.layoutChanged.emit()

class StructListModel(BasicListModel):

    def __init__(self, items, locs, types, *args, **kwargs):
        self.types = types
        self.locs = locs
        super(StructListModel, self).__init__(items)        

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            loc_value = self.items[row].loc.value
            type_value = self.items[row].type.value       

            return "{0} {1}".format(loc_value, type_value)

    def sort(self):
        self.items.sort(key=lambda x: (x.loc, x.type), reverse=False)
        self.layoutChanged.emit()

class RulesListModel(BasicListModel):

    def __init__(self, items, locs, types, freqs, *args, **kwargs):
        self.types = types
        self.locs = locs
        self.freqs = freqs
        super(RulesListModel, self).__init__(items)        

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            loc_from_value = self.items[row].struct_from.loc.value
            type_from_value = self.items[row].struct_from.type.value
            loc_to_value = self.items[row].struct_to.loc.value
            type_to_value = self.items[row].struct_to.type.value
            dir = self.items[row].dir
            freq_value = self.items[row].freq.value
            next_pm = self.items[row].next_pm

            return "From : {0} {1}\nTo : {2} {3}\n{4} month\nNext Pm : {5}{6} month".format(loc_from_value,
                                                                                            type_from_value,
                                                                                            loc_to_value,
                                                                                            type_to_value,
                                                                                            freq_value,
                                                                                            dir,
                                                                                            next_pm)

    def sort(self):
        self.items.sort(key=lambda x: (x.struct_from,
                                       x.struct_to,
                                       x.freq), reverse=False)
        self.layoutChanged.emit()

class PMListModel(BasicListModel):

    def __init__(self, items, freqs, *args, **kwargs):
        super(PMListModel, self).__init__(items)
        self.freqs = freqs

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            date = self.items[row].get_date_to_string()
            freq_id = self.items[row].freq.id     
            freq = next((freq for freq in self.freqs if freq.id == freq_id), None)

            return "{0} {1} month".format(date, freq.value)
    
    def sort(self):
        self.items.sort(key=lambda x: x, reverse=True)
        self.layoutChanged.emit()

class HistListModel(BasicListModel):

    def __init__(self, items, locs, *args, **kwargs):
        super(HistListModel, self).__init__(items)
        self.locs = locs

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            date = self.items[row].get_date_to_string()
            location = self.items[row].loc.value
            return "{0} {1}".format(date, location)

    def sort(self):
        self.items.sort(key=lambda x: x, reverse=True)
        self.layoutChanged.emit()

class BasicComboModel(QtCore.QAbstractListModel):
    def __init__(self, items, *args, **kwargs):
        QtCore.QAbstractListModel.__init__(self, *args, **kwargs)
        self.items = items

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.items)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            value = self.items[row].value
            return "{0}".format(value)

    def getItem(self, row):
        if 0 <= row < self.rowCount():
            return self.items[row]

    def clear(self):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount() - 1)
        self.items = []
        self.endRemoveRows()

class TablePumpModel(QtCore.QAbstractTableModel):
    def __init__(self, datas):
        super(TablePumpModel, self).__init__()
        self.datas = datas
        self.init_table_data()

    def data(self, index, role):
        if role == Qt.DisplayRole:
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
        self.pm_data_table = []

        for struct in self.datas.struct:
                headerH.append(
                    struct.loc.value
                    + "_" 
                    + struct.type.value) 

        for freq in self.datas.freqs:
            pms = []
            headerV.append(str(freq.value) + " month")
            for struct in self.datas.struct:
                text = "N/A"
                freq_in_struc = freq.exist(struct.freqs)  
                if freq_in_struc is not None:  
                    text = "No Pump"            
                    for pump in self.datas.pumps:

                        #Only one pump can be installed (last location is the installed location)
                        #Check what is the last location of the pump
                        actual_loc = pump.get_actual_loc()

                        #Create a Temp Structure with the pump data to compare with the existing structure
                        temp_struct = PMStructure(
                            actual_loc,
                            pump.type,
                            [])

                        #Check if the last installed location is in the structure
                        pump_in_struct = temp_struct.exist([struct])
                        if pump_in_struct is not None:
                            last_text = "Installed :"
                            install_date = next(hist.date for hist in pump.lochistory if hist.loc == actual_loc)
                            lastdate_to_str =  datetime.strftime(install_date, '%Y/%m/%d')  
                            nextdate = install_date + relativedelta(months=int(freq.value))
                            
                            #Check if a pm has already been performed
                            lastdate = pump.get_last_pm_date(freq.id)
                            if lastdate is not None:
                                last_text = "Last :" 
                                lastdate_to_str = lastdate
                                date = datetime.strptime(lastdate, '%Y/%m/%d')
                                nextdate = date + relativedelta(months=int(freq.value))
                            
                            #Check if the pump has previously been installed in an other location.
                            previous_loc_id = pump.get_previous_loc()
                            if previous_loc_id is not None:

                                # Create a temp rule with the old and new pump structure
                                # Check if rules if exist and apply it
                                temp_rule = Rules(
                                    PMStructure(
                                        self.datas.get_obj_by_attr('id', previous_loc_id, "locs"),
                                        self.datas.get_obj(pump.type, "types"),
                                        []
                                    ),
                                    PMStructure(
                                        actual_loc,
                                        self.datas.get_obj(pump.type, "types"),
                                        []
                                    ),
                                    freq,
                                    "",
                                    "").exist(self.datas.rules)
                                    
                                if temp_rule is not None:
                                    if temp_rule.dir == "+":
                                        nextdate = nextdate + relativedelta(months=int(temp_rule.next_pm))
                                    else:
                                        nextdate = nextdate - relativedelta(months=int(temp_rule.next_pm))

                            nextdate_to_str = datetime.strftime(nextdate, '%Y/%m/%d')                            
                            text = "{0} {1}\nNext : {2}\n{3}".format(last_text, lastdate_to_str, nextdate_to_str, pump.serial)
                            break
                            
                pms.append(text)
            self.pm_data_table.append(pms)

        self.tabledata = pd.DataFrame(
            self.pm_data_table,
            columns = headerH,
            index = headerV
        )

class ColorProxy(QtCore.QIdentityProxyModel):
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.BackgroundRole:
            data = index.data()
            if data == "N/A":
                return QtGui.QColor.fromRgb(211, 211, 211)
            elif data == "Never":
                return QtGui.QColor.fromRgb(255, 204, 203)
            else:
                try:
                    dates = data.split("\n")
                    Next_str = dates[1].split(" : ")[1]
                    next_date = datetime.strptime(Next_str, "%Y/%m/%d")
                    today_date = datetime.today()
                    if next_date - timedelta(weeks=1) <= today_date <= next_date + timedelta(weeks=1):
                        return QtGui.QColor.fromRgb(254, 216, 177)
                    elif next_date + timedelta(weeks=1) < today_date :
                        return QtGui.QColor.fromRgb(255, 204, 203)
                    else:
                        return QtGui.QColor.fromRgb(144, 238, 144)
                except:
                    pass
        return super().data(index, role)

def messageBox(title, message):
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(QMessageBox.Critical)
    x = msg.exec_()