from datetime import datetime, timedelta
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
import pandas as pd
from config import outdated_period
from Model.objects import Utility


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
        self.items.sort(key=lambda x: x.value, reverse=False)
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
        if role == QtCore.Qt.DisplayRole and len(self.items[row].lochistory) > 0:
            serial = self.items[row].serial
            type_value = self.items[row].type.value
            loc_value = self.items[row].get_actual_loc().value

            return "{0} {1} {2}".format(loc_value, type_value, serial)

    def sort(self):
        self.items.sort(key=lambda x: (x.get_actual_loc(), x.type), reverse=False)
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
    def __init__(self, items, pumps, freqs, *args, **kwargs):
        self.pumps = pumps
        self.freqs = freqs
        super(RulesListModel, self).__init__(items)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            pump = self.items[row].pump
            freq_value = next(
                freq.value for freq in self.freqs if self.items[row].freq == freq
            )
            next_date = Utility.datetime_to_str(self.items[row].date)

            return "{0} {1}\nFreq : {2} month\nNext Pm : {3}".format(
                pump.type.value, pump.serial, freq_value, next_date
            )

    def sort(self):
        self.items.sort(
            key=lambda x: (
                next(pump for pump in self.pumps if x.pump == pump),
                next(freq for freq in self.freqs if x.freq == freq),
            ),
            reverse=False,
        )
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
            generated = "   "
            com = self.items[row].com
            if "Generated by" in com:
                generated = "[G]"
            date = Utility.datetime_to_str(self.items[row].date)
            freq_id = self.items[row].freq.id
            freq = next(freq for freq in self.freqs if freq.id == freq_id)

            return "{0} {1} {2}month".format(generated, date, freq.value)

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
            date = Utility.datetime_to_str(self.items[row].date)
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


class PumpComboModel(BasicComboModel):
    def __init__(self, items, *args, **kwargs):
        QtCore.QAbstractListModel.__init__(self, *args, **kwargs)
        self.items = items

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            type_value = self.items[row].type.value
            serial = self.items[row].serial
            return "{0} {1}".format(type_value, serial)


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
            headerH.append(struct.loc.value + "_" + struct.type.value)

        for freq in self.datas.freqs:
            pms = []
            headerV.append(str(freq.value) + " month")
            for struct in self.datas.struct:
                text = "N/A"
                freq_in_struc = freq.exist(struct.freqs)
                if freq_in_struc is not None:
                    text = "No Pump"
                    for pump in self.datas.pumps:
                        # Only one pump can be installed (last location is the installed location)
                        # Check what is the last location of the pump
                        # Check if the last installed location is in the structure
                        if pump.struct == struct:
                            # First Check if a PM as already been performed for the specified pump and frequency.
                            # If no PM has been realised, the last date will be the first installed location history date
                            last_date = pump.get_last_pm_date(freq)
                            if last_date is not None:
                                last_text = "Last :"
                            else:
                                last_text = "Installed :"
                                last_date = pump.get_first_installed_hist().date

                            lastdate_to_str = Utility.datetime_to_str(last_date)

                            # Calculate the next PM date
                            nextdate_to_str = pump.get_next_pm_date(
                                freq, self.datas.rules
                            )

                            text = "{0} {1}\nNext : {2}\n{3}".format(
                                last_text,
                                lastdate_to_str,
                                nextdate_to_str,
                                pump.serial,
                            )
                            break

                pms.append(text)
            self.pm_data_table.append(pms)

        self.tabledata = pd.DataFrame(
            self.pm_data_table, columns=headerH, index=headerV
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
                    next_date = Utility.str_to_datetime(Next_str)
                    today_date = datetime.today()
                    if (
                        next_date - timedelta(weeks=outdated_period)
                        <= today_date
                        <= next_date + timedelta(weeks=outdated_period)
                    ):
                        return QtGui.QColor.fromRgb(254, 216, 177)
                    elif next_date + timedelta(weeks=outdated_period) < today_date:
                        return QtGui.QColor.fromRgb(255, 204, 203)
                    else:
                        return QtGui.QColor.fromRgb(144, 238, 144)
                except:
                    pass
        return super().data(index, role)


def messageBox(title, message):
    msg = QMessageBox()
    msg.setStandardButtons(QMessageBox.Close)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(QMessageBox.Critical)
    x = msg.exec_()
