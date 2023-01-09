from Model.model import messageBox, FreqListModel
from Model.objects import Frequency
from View.BasicDialog import BasicDialog


class FreqWindow(BasicDialog):
    """Frequency Window"""

    def __init__(self, parent, *args, **kwargs):
        """Initializer."""
        super(FreqWindow, self).__init__(parent, *args, **kwargs)

    def initmodel(self):
        self.model = FreqListModel(self.datas.freqs)
        self.list.setModel(self.model)

    def deleteclicked(self):
        if len(self.list.selectionModel().selection().indexes()) > 0:
            del_index = self.list.selectionModel().selection().indexes()[0]
            freq_id = self.datas.freqs[del_index.row()].id
            freqtodelete = self.datas.freq(freq_id)
            freq_in_rule = freqtodelete.exist(
                [Frequency(rule.freq.id, rule.freq.value) for rule in self.datas.rules]
            )
            if freq_in_rule is None:
                struct_freqs = []
                for struct in self.datas.struct:
                    struct_freqs.extend(struct.freqs)
                freq_in_struc = freqtodelete.exist(struct_freqs)
                if freq_in_struc is None:
                    pm_freqs = []
                    for pump in self.datas.pumps:
                        pm_freqs.extend([pm.freq for pm in pump.pm])
                    freq_in_pm = freqtodelete.exist(pm_freqs)
                    if freq_in_pm is None:
                        self.model.removeItem(del_index.row())
                        self.datas.save_frequency()
                        self.selectedItem = None
                    else:
                        messageBox(
                            "Frequency used in pm",
                            "You can't delete a frequency used in a pm. Please manage the pm first !",
                        )
                else:
                    messageBox(
                        "Frequency used in structure",
                        "You can't delete a frequency used in the structure. Please update the structure first !",
                    )
            else:
                messageBox(
                    "Frequency used in rules",
                    "You can't delete a frequency used in a rule. Please update the rules first !",
                )
        else:
            messageBox("Selection Error", "Please select a frequency")

    def validateclicked(self):
        if self.text.text() != "":
            if self.text.text().isnumeric():
                temp_frequency = Frequency(0, self.text.text()).exist(self.datas.freqs)
                if temp_frequency is None or temp_frequency == self.selectedItem:
                    if self.actionToken == "Add":
                        self.addFreq()
                        self.resetview()
                    elif self.actionToken == "Modif":
                        if self.selectedItem is not None:
                            self.modifyFreq()
                            self.resetview()
                else:
                    messageBox(
                        "New frequency error",
                        "New Freqcuency can't have the same value that existing frequency !",
                    )
            else:
                messageBox("Frequency Value error", "New Freqcuency must be a number !")
        else:
            messageBox(
                "Missing Information", "Please review the missing information(s)"
            )

    def addFreq(self):
        newid = self.datas.get_new_id("freqs")
        value = int(self.text.text())
        freq = Frequency(newid, value)
        self.model.addItem(freq)
        self.datas.save_frequency()

    def modifyFreq(self):
        selected_id = self.selectedItem.id
        for i, freq in enumerate(self.datas.freqs):
            if freq.id == selected_id:
                self.datas.freqs[i].value = int(self.text.text())
                self.model.updateItem(i, self.datas.freqs[i])
                self.datas.save_frequency()
                break
