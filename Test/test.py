import unittest
from main import MainWindow
from Model.objects import (
    Frequency,
    Type,
    Location,
    Pump,
    LocHistory,
    Utility,
    Structure,
    PM,
    Rules,
    Data,
)
from View.frequency import FreqWindow
from View.type import TypeWindow
from View.location import LocWindow
from View.pumps_window import PumpWindow
from View.history import HistWindow
from View.pm import PMWindow
from View.rules import RulesWindow
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QDate, Qt, QThread, QTimer
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtTest import QTest
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import time


if not QtWidgets.QApplication.instance():
    app = QtWidgets.QApplication([])


class FrequencyDialogs(unittest.TestCase):
    def setUp(self):
        self.data_dir = "test/Data/"
        self.win = MainWindow(self.data_dir)
        self.win.resize_table_to_contents()
        self.win.show()
        self.freqwin = FreqWindow(parent=self.win)
        self.freqwin.setWindowTitle("Frequency")
        self.win.datas.freqs.append(Frequency(1, 1))
        self.freqwin.show()

    def test_Add(self):
        self.freqwin.addbutton.click()
        self.freqwin.text.setText("2")
        self.freqwin.validatebutton.click()

        freq = next(freq for freq in self.win.datas.freqs if freq.id == 2)

        assert freq.value == 2

        with open("{0}frequency.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)
        selected_freq = next(freq for freq in file_content if int(freq["id"]) == 2)
        freq = Frequency(selected_freq["id"], selected_freq["value"])

        assert freq.value == 2

    def test_Modif(self):
        qindex = self.freqwin.model.index(0, 0)
        self.freqwin.list.setCurrentIndex(qindex)
        id = self.freqwin.model.getItem(qindex).id

        self.freqwin.modifbutton.click()
        self.freqwin.text.setText("3")
        self.freqwin.validatebutton.click()

        freq = next(freq for freq in self.win.datas.freqs if freq.id == id)
        assert freq.value == 3

        with open("{0}frequency.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        selected_freq = next(freq for freq in file_content if int(freq["id"]) == id)
        freq = Frequency(selected_freq["id"], selected_freq["value"])
        assert freq.value == 3

    def test_Delete(self):
        qindex = self.freqwin.model.index(0, 0)
        self.freqwin.list.setCurrentIndex(qindex)

        self.freqwin.deletebutton.click()
        assert len(self.win.datas.freqs) == 0

        with open("{0}frequency.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        assert len(file_content) == 0

    def tearDown(self):
        self.win.datas.freqs = []
        self.win.datas.save_frequency()
        self.freqwin.close()
        self.win.close()
        self.win = None
        self.freqwin = None


class TypeDialogs(unittest.TestCase):
    def setUp(self):
        self.data_dir = "test/Data/"
        self.win = MainWindow(self.data_dir)
        self.win.resize_table_to_contents()
        self.win.show()
        self.typewin = TypeWindow(parent=self.win)
        self.typewin.setWindowTitle("Type")
        self.win.datas.types.append(Type(1, "type"))
        self.typewin.show()

    def test_Add(self):
        self.typewin.addbutton.click()
        self.typewin.text.setText("type 2")
        self.typewin.validatebutton.click()

        type = next(type for type in self.win.datas.types if type.id == 2)

        assert type.value == "type 2"

        with open("{0}type.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        selected_type = next(type for type in file_content if int(type["id"]) == 2)
        type = Frequency(selected_type["id"], selected_type["value"])

        assert type.value == "type 2"

    def test_modif(self):
        qindex = self.typewin.model.index(0, 0)
        self.typewin.list.setCurrentIndex(qindex)

        self.typewin.modifbutton.click()
        self.typewin.text.setText("type 3")
        self.typewin.validatebutton.click()

        type = self.win.datas.types[0]
        assert isinstance(type, Type)
        assert type.value == "type 3"

        with open("{0}type.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        type = Type(file_content[0]["id"], file_content[0]["value"])
        assert isinstance(type, Type)
        assert type.value == "type 3"

    def test_Delete(self):
        qindex = self.typewin.model.index(0, 0)
        self.typewin.list.setCurrentIndex(qindex)

        self.typewin.deletebutton.click()
        assert len(self.win.datas.types) == 0

        with open("{0}type.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        assert len(file_content) == 0

    def tearDown(self):
        self.win.datas.types = []
        self.win.datas.save_type()
        self.typewin.close()
        self.win.close()
        self.win = None
        self.typewin = None


class LocationDialogs(unittest.TestCase):
    def setUp(self):
        self.data_dir = "test/Data/"
        self.win = MainWindow(self.data_dir)
        self.win.resize_table_to_contents()
        self.win.show()
        self.locwin = LocWindow(parent=self.win)
        self.locwin.setWindowTitle("Location")
        self.win.datas.locs.append(Location(1, "uninstalled"))
        self.locwin.show()

    def test_Add(self):
        self.locwin.addbutton.click()
        self.locwin.text.setText("location")
        self.locwin.validatebutton.click()

        loc = next(loc for loc in self.win.datas.locs if loc.id == 2)

        assert loc.value == "location"

        with open("{0}location.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        selected_loc = next(loc for loc in file_content if int(loc["id"]) == 2)
        loc = Location(selected_loc["id"], selected_loc["value"])

        assert loc.value == "location"

    def test_Modif(self):
        qindex = self.locwin.model.index(0, 0)
        self.locwin.list.setCurrentIndex(qindex)
        id = self.locwin.model.getItem(qindex).id

        self.locwin.modifbutton.click()
        self.locwin.text.setText("location 2")
        self.locwin.validatebutton.click()

        loc = next(loc for loc in self.win.datas.locs if loc.id == id)
        assert loc.value == "location 2"

        with open("{0}location.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        selected_loc = next(loc for loc in file_content if int(loc["id"]) == id)
        loc = Location(selected_loc["id"], selected_loc["value"])
        assert loc.value == "location 2"

    def test_Delete(self):
        qindex = self.locwin.model.index(0, 0)
        self.locwin.list.setCurrentIndex(qindex)

        self.locwin.deletebutton.click()
        assert len(self.win.datas.locs) == 0

        with open("{0}location.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        assert len(file_content) == 0

    def tearDown(self):
        self.win.datas.locs = []
        self.win.datas.save_location()
        self.locwin.close()
        self.win.close()
        self.win = None
        self.locwin = None


class PumpDialogs(unittest.TestCase):
    def setUp(self):
        self.data_dir = "test/Data/"
        self.dialog_title = ""
        self.win = MainWindow(self.data_dir)
        self.win.resize_table_to_contents()
        self.win.show()

        self.win.datas.types.append(Type(1, "type"))
        self.win.datas.freqs.append(Frequency(1, 1))
        self.win.datas.locs.append(Location(1, "Uninstalled"))
        self.win.datas.locs.append(Location(2, "location 1"))
        self.win.datas.locs.append(Location(3, "location 2"))
        uninstalled = next(loc for loc in self.win.datas.locs if loc.id == 1)
        self.win.datas.struct.append(
            Structure(
                self.win.datas.locs[1],
                self.win.datas.types[0],
                self.win.datas.freqs,
                [],
            )
        )
        self.win.datas.struct.append(
            Structure(
                self.win.datas.locs[2],
                self.win.datas.types[0],
                self.win.datas.freqs,
                [],
            )
        )
        hist = LocHistory(1, 1, uninstalled, Utility.datetime_to_str(datetime.today()))
        self.win.datas.pumps.append(
            Pump(
                1,
                self.win.datas.types[0],
                "serial",
                [],
                ([hist], self.win.datas.struct),
            )
        )
        self.win.datas.history.append(hist)
        self.pumpwin = PumpWindow(parent=self.win)
        self.pumpwin.show()

    def test_Add(self):
        self.pumpwin.addbutton.click()
        index = self.pumpwin.typecombo.findText("type", QtCore.Qt.MatchFixedString)
        self.pumpwin.typecombo.setCurrentIndex(index)
        self.pumpwin.lineserial.setText("serial 2")
        self.pumpwin.historymodel.items.append(
            LocHistory(
                2,
                2,
                next(loc for loc in self.win.datas.locs if loc.id == 2),
                Utility.datetime_to_str(datetime.today()),
            )
        )

        self.pumpwin.validatebutton.click()

        assert len(self.win.datas.pumps) == 2

        pump = next(pump for pump in self.win.datas.pumps if pump.id == 2)

        assert pump.type.id == 1
        assert pump.serial == "serial 2"

        with open("{0}pump.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        selected_pump = next(pump for pump in file_content if int(pump["id"]) == 2)
        pump = Pump(
            selected_pump["id"],
            self.win.datas.type(int(selected_pump["type_id"])),
            selected_pump["serial"],
            [],
            (
                [],
                self.win.datas.struct,
            ),
        )

        assert pump.type.id == 1
        assert pump.serial == "serial 2"

    def test_add_missing_info(self):
        self.pumpwin.addpumpclicked()
        qTimer = QTimer(self.pumpwin)
        qTimer.timeout.connect(self.handleQMessageBox)
        qTimer.start(100)
        self.pumpwin.validateclicked()

        assert self.dialog_title == "Missing Information"
        assert len(self.win.datas.pumps) == 1

    def test_add_missing_info2(self):
        self.pumpwin.addpumpclicked()
        self.pumpwin.lineserial.setText("serial")
        qTimer = QTimer(self.pumpwin)
        qTimer.timeout.connect(self.handleQMessageBox)
        qTimer.start(100)
        self.pumpwin.validateclicked()

        assert self.dialog_title == "Missing Information"
        assert len(self.win.datas.pumps) == 1

    def test_add_missing_info3(self):
        self.pumpwin.addpumpclicked()
        self.pumpwin.typecombo.setCurrentIndex(0)
        qTimer = QTimer(self.pumpwin)
        qTimer.timeout.connect(self.handleQMessageBox)
        qTimer.start(100)
        self.pumpwin.validateclicked()

        assert self.dialog_title == "Missing Information"
        assert len(self.win.datas.pumps) == 1

    def test_add_missing_info3(self):
        self.pumpwin.addpumpclicked()
        self.pumpwin.lineserial.setText("serial")
        self.pumpwin.typecombo.setCurrentIndex(0)
        qTimer = QTimer(self.pumpwin)
        qTimer.timeout.connect(self.handleQMessageBox)
        qTimer.start(100)
        self.pumpwin.validateclicked()

        assert self.dialog_title == "Missing Information"
        assert len(self.win.datas.pumps) == 1

    def test_add_existing(self):
        self.pumpwin.addpumpclicked()
        self.pumpwin.lineserial.setText("serial")
        self.pumpwin.typecombo.setCurrentIndex(0)
        self.pumpwin.historymodel.addItem(
            LocHistory(
                1, 0, Location(1, "loc"), Utility.datetime_to_str(datetime.today())
            )
        )
        qTimer = QTimer(self.pumpwin)
        qTimer.timeout.connect(self.handleQMessageBox)
        qTimer.start(100)
        self.pumpwin.validateclicked()

        assert self.dialog_title == "Existing pump"
        assert len(self.win.datas.pumps) == 1

    def test_add_location_not_free(self):
        hist = LocHistory(
            1, 1, self.win.datas.loc(2), Utility.datetime_to_str(datetime.today())
        )
        self.win.datas.pumps.append(
            Pump(
                1,
                self.win.datas.types[0],
                "serial",
                [],
                ([hist], self.win.datas.struct),
            )
        )
        self.pumpwin.addpumpclicked()
        self.pumpwin.lineserial.setText("serial2")
        self.pumpwin.typecombo.setCurrentIndex(0)

        self.pumpwin.historymodel.addItem(
            LocHistory(
                1, 1, self.win.datas.loc(2), Utility.datetime_to_str(datetime.today())
            )
        )
        qTimer = QTimer(self.pumpwin)
        qTimer.timeout.connect(self.handleQMessageBox)
        qTimer.start(100)
        self.pumpwin.validateclicked()
        assert self.dialog_title == "Location not free"
        assert len(self.win.datas.pumps) == 2

    def test_Modif(self):
        qindex = self.pumpwin.pumpmodel.index(0, 0)
        self.pumpwin.pumplist.setCurrentIndex(qindex)
        id = self.pumpwin.pumpmodel.getItem(qindex).id

        self.pumpwin.modifbutton.click()
        self.pumpwin.lineserial.setText("serial 3")
        self.pumpwin.validatebutton.click()

        pump = next(pump for pump in self.win.datas.pumps if pump.id == id)
        assert pump.serial == "serial 3"

        with open("{0}pump.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        selected_pump = next(pump for pump in file_content if int(pump["id"]) == id)
        pump = Pump(
            selected_pump["id"],
            self.win.datas.type(int(selected_pump["type_id"])),
            selected_pump["serial"],
            [],
            (
                [],
                self.win.datas.struct,
            ),
        )

        assert pump.serial == "serial 3"

    def test_Delete(self):

        qindex = self.pumpwin.pumpmodel.index(0, 0)
        self.pumpwin.pumplist.setCurrentIndex(qindex)

        self.pumpwin.deletebutton.click()
        assert len(self.win.datas.pumps) == 0

        with open("{0}history.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        assert len(file_content) == 0

    def handleQMessageBox(self):
        widget = app.activeModalWidget()
        self.dialog_title = widget.windowTitle()
        widget.close()

    def tearDown(self):
        self.win.datas.pumps = []
        self.win.datas.save_pump()
        self.pumpwin.close()
        self.win.close()
        self.win = None
        self.pumpwin = None


class HistoryDialogs(unittest.TestCase):
    def setUp(self):
        self.data_dir = "test/Data/"
        self.win = MainWindow(self.data_dir)
        self.win.resize_table_to_contents()
        self.win.show()

        self.win.datas.types.append(Type(1, "type"))
        self.win.datas.freqs.append(Frequency(1, 1))
        self.win.datas.locs.append(Location(1, "Uninstalled"))
        self.win.datas.locs.append(Location(2, "location 1"))
        self.win.datas.locs.append(Location(3, "location 2"))
        uninstalled = next(loc for loc in self.win.datas.locs if loc.id == 1)
        self.win.datas.struct.append(
            Structure(
                self.win.datas.locs[1],
                self.win.datas.types[0],
                self.win.datas.freqs,
                [],
            )
        )
        self.win.datas.struct.append(
            Structure(
                self.win.datas.locs[2],
                self.win.datas.types[0],
                self.win.datas.freqs,
                [],
            )
        )
        loc = LocHistory(1, 1, uninstalled, Utility.datetime_to_str(datetime.today()))
        self.win.datas.pumps.append(
            Pump(
                1,
                self.win.datas.types[0],
                "serial",
                [],
                ([loc], self.win.datas.struct),
            )
        )
        self.win.datas.history.append(loc)
        self.pumpwin = PumpWindow(parent=self.win)
        self.pumpwin.show()

        self.histwin = HistWindow(self.win.datas.pumps[0], parent=self.pumpwin)
        self.histwin.show()

    def test_Add(self):
        self.histwin.addbutton.click()
        index = self.histwin.loccombo.findText("location 1", QtCore.Qt.MatchFixedString)
        self.histwin.loccombo.setCurrentIndex(index)
        self.histwin.locdate.setDate(QDate(datetime.today() + relativedelta(days=1)))
        self.histwin.validatebutton.click()

        hist = next(hist for hist in self.win.datas.history if hist.id == 2)

        assert hist.pump_id == 1
        assert hist.loc.value == "location 1"
        assert Utility.datetime_to_str(hist.date) == Utility.datetime_to_str(
            datetime.today() + relativedelta(days=1)
        )

        with open("{0}history.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        selected_hist = next(hist for hist in file_content if int(hist["id"]) == 2)
        hist = LocHistory(
            selected_hist["id"],
            selected_hist["pump_id"],
            next(
                loc
                for loc in self.win.datas.locs
                if loc.id == int(selected_hist["loc_id"])
            ),
            selected_hist["date"],
        )

        assert hist.pump_id == 1
        assert hist.loc.value == "location 1"
        assert Utility.datetime_to_str(hist.date) == Utility.datetime_to_str(
            datetime.today() + relativedelta(days=1)
        )

    def test_Modif(self):
        qindex = self.histwin.model.index(0, 0)
        self.histwin.loclist.setCurrentIndex(qindex)
        id = self.histwin.model.getItem(qindex).id

        self.histwin.modifbutton.click()
        self.histwin.locdate.setDate(QDate(datetime.today() + relativedelta(days=2)))
        self.histwin.validatebutton.click()

        hist = next(hist for hist in self.win.datas.history if hist.id == id)
        assert Utility.datetime_to_str(hist.date) == Utility.datetime_to_str(
            datetime.today() + relativedelta(days=2)
        )

        with open("{0}history.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        selected_hist = next(hist for hist in file_content if int(hist["id"]) == id)
        hist = LocHistory(
            selected_hist["id"],
            selected_hist["pump_id"],
            next(
                loc
                for loc in self.win.datas.locs
                if loc.id == int(selected_hist["loc_id"])
            ),
            selected_hist["date"],
        )
        assert Utility.datetime_to_str(hist.date) == Utility.datetime_to_str(
            datetime.today() + relativedelta(days=2)
        )

    def test_Delete(self):
        self.histwin.addbutton.click()
        index = self.histwin.loccombo.findText("location 1", QtCore.Qt.MatchFixedString)
        self.histwin.loccombo.setCurrentIndex(index)
        self.histwin.locdate.setDate(QDate(datetime.today() + relativedelta(days=2)))

        self.histwin.validatebutton.click()

        for i, hist in enumerate(self.histwin.model.items):
            if hist.loc.value == "location 1":
                qindex = self.histwin.model.index(i, 0)
                break
        self.histwin.loclist.setCurrentIndex(qindex)

        self.histwin.deletebutton.click()
        assert len(self.win.datas.history) == 1
        hist = self.win.datas.history[0]

        assert hist.loc.value == "location 1"

        with open("{0}history.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        hist = LocHistory(
            file_content[0]["id"],
            file_content[0]["pump_id"],
            next(
                loc
                for loc in self.win.datas.locs
                if loc.id == int(file_content[0]["loc_id"])
            ),
            file_content[0]["date"],
        )
        assert len(file_content) == 1
        assert hist.loc.value == "location 1"

    def tearDown(self):
        self.win.datas.history = []
        self.win.datas.save_history()
        self.histwin.close()
        self.pumpwin.close()
        self.win.close()
        self.win = None
        self.pumpwin = None
        self.histwin = None


class PMDialogs(unittest.TestCase):
    def setUp(self):
        self.data_dir = "test/Data/"
        self.win = MainWindow(self.data_dir)
        self.win.resize_table_to_contents()
        self.win.show()

        self.win.datas.types.append(Type(1, "type"))
        self.win.datas.freqs.append(Frequency(1, 1))
        self.win.datas.locs.append(Location(1, "Uninstalled"))
        self.win.datas.locs.append(Location(2, "location 1"))
        self.win.datas.locs.append(Location(3, "location 2"))
        loc1 = next(loc for loc in self.win.datas.locs if loc.id == 2)
        self.win.datas.history.append(
            LocHistory(
                1, 1, self.win.datas.locs[1], Utility.datetime_to_str(datetime.today())
            )
        )
        self.win.datas.struct.append(
            Structure(
                next(loc for loc in self.win.datas.locs if loc.id == 2),
                self.win.datas.types[0],
                self.win.datas.freqs,
                [],
            )
        )
        pm = PM(
            1,
            1,
            self.win.datas.freqs[0],
            Utility.datetime_to_str(datetime.today()),
            "com",
        )
        hist = LocHistory(1, 1, loc1, Utility.datetime_to_str(datetime.today()))
        self.win.datas.pumps.append(
            Pump(
                1,
                self.win.datas.types[0],
                "serial",
                [pm],
                ([hist], self.win.datas.struct),
            )
        )
        self.win.datas.pm.append(pm)
        self.win.datas.history.append(hist)
        self.pumpwin = PumpWindow(parent=self.win)

        self.pmwin = PMWindow(self.win.datas.pumps[0], parent=self.pumpwin)
        self.pmwin.show()

    def test_add(self):
        self.pmwin.addbutton.click()
        self.pmwin.pmdate.setDate(QDate(datetime.today() + relativedelta(days=1)))
        self.pmwin.freqcombo.setCurrentIndex(0)
        self.pmwin.comtext.setPlainText("com")

        self.pmwin.validatebutton.click()

        pm = next(pm for pm in self.win.datas.pm if pm.id == 2)

        assert pm.pump_id == 1
        assert pm.freq.value == 1
        assert Utility.datetime_to_str(pm.date) == Utility.datetime_to_str(
            datetime.today() + relativedelta(days=1)
        )
        assert pm.com == "com"

        with open("{0}pm.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        selected_pm = next(pm for pm in file_content if int(pm["id"]) == 2)
        pm = PM(
            selected_pm["id"],
            selected_pm["pump_id"],
            next(
                freq
                for freq in self.win.datas.freqs
                if freq.id == int(selected_pm["freq_id"])
            ),
            selected_pm["date"],
            selected_pm["com"],
        )

        assert pm.pump_id == 1
        assert pm.freq.value == 1
        assert Utility.datetime_to_str(pm.date) == Utility.datetime_to_str(
            datetime.today() + relativedelta(days=1)
        )
        assert pm.com == "com"

    def test_Modif(self):
        qindex = self.pmwin.model.index(0, 0)
        self.pmwin.pmlist.setCurrentIndex(qindex)
        id = self.pmwin.model.getItem(qindex).id

        self.pmwin.modifbutton.click()
        self.pmwin.pmdate.setDate(QDate(datetime.today() + relativedelta(days=2)))
        self.pmwin.validatebutton.click()

        pm = next(pm for pm in self.win.datas.pm if pm.id == id)
        assert Utility.datetime_to_str(pm.date) == Utility.datetime_to_str(
            datetime.today() + relativedelta(days=2)
        )

        with open("{0}pm.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        selected_pm = next(pm for pm in file_content if int(pm["id"]) == id)
        pm = PM(
            selected_pm["id"],
            selected_pm["pump_id"],
            next(
                freq
                for freq in self.win.datas.freqs
                if freq.id == int(selected_pm["freq_id"])
            ),
            selected_pm["date"],
            selected_pm["com"],
        )
        assert Utility.datetime_to_str(pm.date) == Utility.datetime_to_str(
            datetime.today() + relativedelta(days=2)
        )

    def test_delete(self):
        qindex = self.pmwin.model.index(0, 0)
        self.pmwin.pmlist.setCurrentIndex(qindex)
        self.pmwin.deletebutton.click()
        assert len(self.win.datas.pm) == 0

        with open("{0}pm.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        assert len(file_content) == 0

    def tearDown(self):
        self.win.datas.pm = []
        self.win.datas.save_pm()
        self.pmwin.close()
        self.win.close()
        self.win = None
        self.pmwin = None


class RuleDialogs(unittest.TestCase):
    def setUp(self):
        self.data_dir = "test/Data/"
        self.win = MainWindow(self.data_dir)
        self.win.resize_table_to_contents()
        self.win.show()

        self.win.datas.types.append(Type(1, "type"))
        self.win.datas.freqs.append(Frequency(1, 1))
        self.win.datas.locs.append(Location(1, "Uninstalled"))
        self.win.datas.locs.append(Location(2, "location 1"))
        loc = next(loc for loc in self.win.datas.locs if loc.id == 2)
        hist = LocHistory(1, 1, loc, Utility.datetime_to_str(datetime.today()))
        self.win.datas.history.append(hist)
        self.win.datas.struct.append(
            Structure(
                loc,
                self.win.datas.types[0],
                self.win.datas.freqs,
                [],
            )
        )
        self.win.datas.pumps.append(
            Pump(
                1,
                self.win.datas.types[0],
                "serial",
                [],
                ([hist], self.win.datas.struct),
            )
        )
        self.win.datas.history.append(hist)
        self.win.datas.rules.append(
            Rules(
                1,
                self.win.datas.pumps[0],
                self.win.datas.freqs[0],
                Utility.datetime_to_str(datetime.today()),
                True,
            )
        )
        self.rulewin = RulesWindow(parent=self.win)
        self.rulewin.show()

    def test_add(self):
        self.rulewin.addbutton.click()
        self.rulewin.pumpcombo.setCurrentIndex(0)
        self.rulewin.combo.setCurrentIndex(0)
        self.rulewin.date.setDate(QDate(datetime.today() + relativedelta(days=1)))
        self.rulewin.check.setChecked(True)
        self.rulewin.validatebutton.click()

        rule = next(rule for rule in self.win.datas.rules if rule.id == 2)

        assert rule.pump.id == 1
        assert rule.freq.id == 1
        assert Utility.datetime_to_str(rule.date) == Utility.datetime_to_str(
            datetime.today() + relativedelta(days=1)
        )
        assert rule.synchro == True

        with open("{0}rules.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        selected_rule = next(rule for rule in file_content if int(rule["id"]) == 2)
        rule = Rules(
            selected_rule["id"],
            self.win.datas.pump(int(selected_rule["pump_id"])),
            self.win.datas.freq(int(selected_rule["freq_id"])),
            selected_rule["date"],
            selected_rule["synchro"],
        )

        assert rule.pump.id == 1
        assert rule.freq.id == 1
        assert Utility.datetime_to_str(rule.date) == Utility.datetime_to_str(
            datetime.today() + relativedelta(days=1)
        )
        assert rule.synchro == True

    def test_Modif(self):
        qindex = self.rulewin.rulesmodel.index(0, 0)
        self.rulewin.list.setCurrentIndex(qindex)
        id = self.rulewin.rulesmodel.getItem(qindex).id

        self.rulewin.modifbutton.click()
        self.rulewin.date.setDate(QDate(datetime.today() + relativedelta(days=2)))
        self.rulewin.validatebutton.click()

        rule = next(rule for rule in self.win.datas.rules if rule.id == id)
        assert Utility.datetime_to_str(rule.date) == Utility.datetime_to_str(
            datetime.today() + relativedelta(days=2)
        )

        with open("{0}rules.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        selected_rule = next(rule for rule in file_content if int(rule["id"]) == id)
        rule = Rules(
            selected_rule["id"],
            self.win.datas.pump(int(selected_rule["pump_id"])),
            self.win.datas.freq(int(selected_rule["freq_id"])),
            selected_rule["date"],
            selected_rule["synchro"],
        )
        assert Utility.datetime_to_str(rule.date) == Utility.datetime_to_str(
            datetime.today() + relativedelta(days=2)
        )

    def test_delete(self):
        qindex = self.rulewin.rulesmodel.index(0, 0)
        self.rulewin.list.setCurrentIndex(qindex)
        self.rulewin.deletebutton.click()
        assert len(self.win.datas.rules) == 0

        with open("{0}rules.json".format(self.data_dir), "r") as openfile:
            file_content = json.load(openfile)

        assert len(file_content) == 0

    def tearDown(self):
        self.win.datas.rules = []
        self.win.datas.save_rules()
        self.rulewin.close()
        self.win.close()
        self.win = None
        self.rulewin = None


class PumpTest(unittest.TestCase):
    def setUp(self):
        self.datas = Data("test/Data/")
        self.datas.types.append(Type(1, "type"))
        self.datas.freqs.append(Frequency(1, 1))
        self.datas.freqs.append(Frequency(2, 6))
        self.datas.locs.append(Location(1, "Uninstalled"))
        self.datas.locs.append(Location(2, "location 1"))
        self.datas.locs.append(Location(3, "location 2"))
        loc = self.datas.loc(2)
        loc2 = self.datas.loc(3)
        self.datas.struct.append(
            Structure(
                loc,
                self.datas.type(1),
                self.datas.freqs,
                [],
            )
        )
        self.datas.struct.append(
            Structure(
                loc2,
                self.datas.type(1),
                self.datas.freqs,
                [
                    {"id": "1", "freq_id_associated": []},
                    {"id": "2", "freq_id_associated": ["1"]},
                ],
            )
        )
        hist = LocHistory(1, 1, loc, Utility.datetime_to_str(datetime.today()))
        hist2 = LocHistory(
            2,
            1,
            loc2,
            Utility.datetime_to_str(datetime.today() + relativedelta(days=1)),
        )
        pm = PM(
            1,
            1,
            self.datas.freqs[0],
            Utility.datetime_to_str(datetime.today()),
            "com",
        )
        pm1 = PM(
            2,
            1,
            self.datas.freqs[0],
            Utility.datetime_to_str(datetime.today() + relativedelta(days=1)),
            "com",
        )
        self.pump = Pump(
            1,
            self.datas.types[0],
            "serial",
            [pm, pm1],
            ([hist, hist2], self.datas.struct),
        )
        self.datas.pumps.append(self.pump)
        self.datas.history.append(hist)
        self.datas.history.append(hist2)

    def test_struct(self):
        assert self.pump.struct == self.datas.struct[1]

    def test_actual_loc(self):
        assert self.pump.get_actual_loc() == self.datas.loc(3)

    def test_last_installed_hist(self):
        assert self.pump.get_last_installed_hist() == next(
            hist for hist in self.datas.history if hist.loc.id == 3
        )

    def test_first_installed_hist(self):
        assert self.pump.get_first_installed_hist() == next(
            hist for hist in self.datas.history if hist.loc.id == 2
        )

    def test_last_pm_date(self):
        freq = self.datas.freq(1)
        assert Utility.datetime_to_str(
            self.pump.get_last_pm_date(freq)
        ) == Utility.datetime_to_str(datetime.today() + relativedelta(days=1))

    def test_next_pm_date_1(self):
        freq = self.datas.freq(1)
        assert self.pump.get_next_pm_date(freq, []) == Utility.datetime_to_str(
            datetime.today() + relativedelta(months=1)
        )

    def test_next_pm_date_2(self):
        freq = self.datas.freq(1)
        self.datas.rules.append(
            Rules(
                1,
                self.pump,
                freq,
                Utility.datetime_to_str(datetime.today() + relativedelta(days=3)),
                False,
            )
        )
        assert self.pump.get_next_pm_date(
            freq,
            self.datas.rules,
        ) == Utility.datetime_to_str(datetime.today() + relativedelta(days=3))

    def test_next_pm_date_3(self):
        freq = self.datas.freq(1)
        self.datas.rules.append(
            Rules(
                1,
                self.pump,
                freq,
                Utility.datetime_to_str(datetime.today() - relativedelta(days=3)),
                False,
            )
        )
        assert self.pump.get_next_pm_date(
            freq,
            self.datas.rules,
        ) == Utility.datetime_to_str(datetime.today() + relativedelta(months=1))

    def test_next_pm_date_4(self):
        freq = self.datas.freq(1)
        self.datas.rules.append(
            Rules(
                1,
                self.pump,
                freq,
                Utility.datetime_to_str(datetime.today() - relativedelta(days=3)),
                True,
            )
        )
        assert self.pump.get_next_pm_date(
            freq,
            self.datas.rules,
        ) == Utility.datetime_to_str(
            datetime.today() + relativedelta(months=1) - relativedelta(days=3)
        )

    def test_next_pm_date_5(self):
        freq = self.datas.freq(1)
        self.datas.rules.append(
            Rules(
                1,
                self.pump,
                freq,
                Utility.datetime_to_str(datetime.today() + relativedelta(months=2)),
                False,
            )
        )
        assert self.pump.get_next_pm_date(
            freq,
            self.datas.rules,
        ) == Utility.datetime_to_str(datetime.today() + relativedelta(months=2))

    def test_next_pm_date_6(self):
        freq = self.datas.freq(1)
        freq2 = self.datas.freq(2)
        rule = Rules(
            1,
            self.pump,
            freq,
            Utility.datetime_to_str(datetime.today() + relativedelta(days=3)),
            True,
        )
        self.datas.rules.append(rule)
        assert self.pump.get_next_pm_date(
            freq2,
            self.datas.rules,
        ) == Utility.datetime_to_str(
            datetime.today() + relativedelta(months=5) + relativedelta(days=3)
        )

    def test_next_pm_date_7(self):
        freq = self.datas.freq(1)
        freq2 = self.datas.freq(2)
        rule = Rules(
            1,
            self.pump,
            freq,
            Utility.datetime_to_str(datetime.today() + relativedelta(months=7)),
            True,
        )
        self.datas.rules.append(rule)
        assert self.pump.get_next_pm_date(
            freq2,
            self.datas.rules,
        ) == Utility.datetime_to_str(datetime.today() + relativedelta(months=6))

    def test_next_pm_date_8(self):
        freq = self.datas.freq(1)
        freq2 = self.datas.freq(2)
        rule = Rules(
            1,
            self.pump,
            freq,
            Utility.datetime_to_str(datetime.today() + relativedelta(months=2)),
            True,
        )
        rule2 = Rules(
            1,
            self.pump,
            freq2,
            Utility.datetime_to_str(datetime.today() - relativedelta(months=1)),
            False,
        )
        rule3 = Rules(
            1,
            self.pump,
            freq2,
            Utility.datetime_to_str(datetime.today() + relativedelta(months=1)),
            False,
        )
        self.datas.rules.append(rule)
        self.datas.rules.append(rule2)
        self.datas.rules.append(rule3)

        assert self.pump.get_next_pm_date(
            freq2,
            self.datas.rules,
        ) == Utility.datetime_to_str(datetime.today() + relativedelta(months=1))

    def test_location_is_free(self):
        loc = self.datas.loc(2)
        hist = LocHistory(1, 1, loc, Utility.datetime_to_str(datetime.today()))
        pump = Pump(
            2,
            self.datas.type(1),
            "serial 2",
            [],
            ([hist], self.datas.struct),
        )
        assert pump.location_free(self.datas.pumps) is True

    def test_location_is_not_free(self):
        loc = self.datas.loc(3)
        hist = LocHistory(1, 1, loc, Utility.datetime_to_str(datetime.today()))
        pump = Pump(
            2,
            self.datas.type(1),
            "serial 2",
            [],
            ([hist], self.datas.struct),
        )
        assert pump.location_free(self.datas.pumps) is False

    def test_not_only_uninstalled(self):
        assert self.datas.pump(1).not_only_uninstalled() is True

    def test_only_uninstalled(self):
        loc = self.datas.loc(1)
        hist = LocHistory(1, 1, loc, Utility.datetime_to_str(datetime.today()))
        pump = Pump(
            2,
            self.datas.type(1),
            "serial 2",
            [],
            ([hist], self.datas.struct),
        )
        assert pump.not_only_uninstalled() is False

    def test_active_rule(self):
        rule = Rules(
            1,
            self.datas.pump(1),
            self.datas.freq(1),
            Utility.datetime_to_str(datetime.today() + relativedelta(days=5)),
            False,
        )
        assert self.datas.pump(1).get_active_rule(self.datas.freq(1), [rule]) == rule

    def test_active_rule2(self):
        rule = Rules(
            1,
            self.datas.pump(1),
            self.datas.freq(1),
            Utility.datetime_to_str(datetime.today() + relativedelta(days=1)),
            False,
        )
        rule2 = Rules(
            1,
            self.datas.pump(1),
            self.datas.freq(1),
            Utility.datetime_to_str(datetime.today() + relativedelta(days=5)),
            False,
        )
        assert (
            self.datas.pump(1).get_active_rule(self.datas.freq(1), [rule, rule2])
            == rule2
        )

    def test_active_rule3(self):
        rule = Rules(
            1,
            self.datas.pump(1),
            self.datas.freq(1),
            Utility.datetime_to_str(datetime.today() - relativedelta(days=1)),
            False,
        )
        rule2 = Rules(
            1,
            self.datas.pump(1),
            self.datas.freq(1),
            Utility.datetime_to_str(datetime.today() + relativedelta(days=5)),
            False,
        )
        assert (
            self.datas.pump(1).get_active_rule(self.datas.freq(1), [rule, rule2])
            == rule2
        )

    def test_active_rule4(self):
        rule = Rules(
            1,
            self.datas.pump(1),
            self.datas.freq(1),
            Utility.datetime_to_str(datetime.today() - relativedelta(days=1)),
            False,
        )

        assert self.datas.pump(1).get_active_rule(self.datas.freq(1), [rule]) is None

    def test_active_rule5(self):
        rule = Rules(
            1,
            self.datas.pump(1),
            self.datas.freq(1),
            Utility.datetime_to_str(datetime.today() + relativedelta(days=1)),
            True,
        )
        rule2 = Rules(
            1,
            self.datas.pump(1),
            self.datas.freq(1),
            Utility.datetime_to_str(datetime.today() + relativedelta(days=5)),
            False,
        )
        assert (
            self.datas.pump(1).get_active_rule(self.datas.freq(1), [rule, rule2])
            == rule2
        )

    def test_active_rule6(self):
        rule = Rules(
            1,
            self.datas.pump(1),
            self.datas.freq(1),
            Utility.datetime_to_str(datetime.today() - relativedelta(days=1)),
            True,
        )

        assert self.datas.pump(1).get_active_rule(self.datas.freq(1), [rule]) == rule

    def test_active_rule6(self):
        rule = Rules(
            1,
            self.datas.pump(1),
            self.datas.freq(1),
            Utility.datetime_to_str(datetime.today() - relativedelta(days=1)),
            True,
        )

        assert self.datas.pump(1).get_active_rule(self.datas.freq(2), [rule]) == rule

    def test_get_associated_pm(self):
        pm = PM(
            3,
            1,
            self.datas.freq(2),
            Utility.datetime_to_str(datetime.today()),
            "com",
        )
        pm1 = PM(
            4,
            1,
            self.datas.freq(1),
            Utility.datetime_to_str(datetime.today()),
            "Generated by",
        )
        self.datas.pump(1).pm.append(pm)
        self.datas.pump(1).pm.append(pm1)
        assert self.datas.pump(1).get_associated_pm(pm, [1]) == [pm1]


class StructureTest(unittest.TestCase):
    def setUp(self):
        self.datas = Data("test/Data/")
        self.datas.types.append(Type(1, "type"))

        self.datas.locs.append(Location(2, "location 1"))
        loc = self.datas.loc(2)
        self.struct = Structure(
            loc,
            self.datas.type(1),
            self.datas.freqs,
            [
                {"id": "1", "freq_id_associated": []},
                {"id": "2", "freq_id_associated": ["1"]},
            ],
        )

    def test_freq_associated_id(self):
        assert self.struct.freq_associated_id(2) == [1]


if __name__ == "__main__":
    unittest.main()
