import json
import os
from datetime import datetime
from dateutil.parser import parse
from config import continuous_installation_time
from dateutil.relativedelta import relativedelta


class Pump:
    def __init__(self, id, type, serial, pms=None, lochistory=None):
        """
        init expect : pump type,
        """
        self.id = int(id)
        self.type = type
        self.serial = serial
        self.pm = pms
        self._struct = None
        self.lochistory = lochistory

    @property
    def lochistory(self):
        return self._lochistory

    @property
    def struct(self):
        return self._struct

    @lochistory.setter
    def lochistory(self, values):
        """
        Location history
        When setting this attribute, we want to pass also the structure, so we can connect the pump to a known structure
        """
        try:
            lochistory, all_struct = values
        except ValueError:
            raise ValueError("Pass an iterable with two items")
        else:
            """This will run only if no exception was raised"""
            self._lochistory = lochistory
            self._set_instance_struc(all_struct)

    def _set_instance_struc(self, all_struct):
        """Pump stuct depends on its last location"""
        hist = self._get_last_hist()
        if hist is not None:
            self._struct = next(
                (
                    struct
                    for struct in all_struct
                    if hist.loc == struct.loc and self.type == struct.type
                ),
                None,
            )

    def __eq__(self, other):
        return self.serial.lower() == other.serial.lower() or self.id == other.id

    def __lt__(self, obj):
        return (self.get_actual_loc(), self.type) < (obj.get_actual_loc(), obj.type)

    def dump(self):
        return {"id": self.id, "type_id": self.type.id, "serial": self.serial}

    def exist(self, pumps):
        for pump in pumps:
            if pump == self:
                return pump
        return None

    def get_actual_loc(self):
        """This will return the last location of the pump. the most recent in time"""
        if len(self.lochistory) > 0:
            return next(
                (
                    hist.loc
                    for hist in self.lochistory
                    if hist.date == max([hist.date for hist in self.lochistory])
                ),
                None,
            )
        return None

    def get_last_installed_hist(self):
        """Return the last installed location history. Uninstalled won't be returned"""
        if len(self.lochistory) > 0:
            installed_hist = [hist for hist in self.lochistory if hist.loc.id != 1]
            if len(installed_hist) > 0:
                return max(installed_hist)

        return None

    def get_first_installed_hist(self):
        """Return the first installed location history"""
        if len(self.lochistory) > 0:
            installed_hist = [hist for hist in self.lochistory if hist.loc.id != 1]
            if len(installed_hist) > 0:
                return min(installed_hist)

        return None

    def get_last_pm_date(self, freq):
        """Return the last PM date at specific frequency"""
        last_pm = self._get_last_pm(freq)
        if last_pm is not None:
            return last_pm.date
        return None

    def get_next_pm_date(self, freq, rules):
        """
        Parameter:  freq : Frequency
                    rules : List of rules

        Calculate the date of the next PM to be done at specific frequency.
        If a rule exist, it will be applied

        return str
        """
        # The pump as to be in the struct to get PM frequencies
        if self._struct is not None:
            # Check if a rule exist for this pump
            active_rule = self.get_active_rule(freq, rules)
            if active_rule is not None:
                # Check if the active rule is at the same frequency than the PM
                if active_rule.freq == freq:
                    # if the rule did not happened yet, the next PM will be at the rule date
                    if active_rule.date > datetime.today():
                        next_pm_date = active_rule.date
                    else:
                        # else the origin to calculate the next PM will be the rule date
                        next_pm_date = self._calculate_next_pm_date(
                            freq, active_rule.date
                        )
                else:
                    # First calculate the next PM from the installation date.
                    # If the next PM happen prior to the rule date, the normal calculation will be kept.
                    # else the rule date will be use as origin date and the next PM date will be recalculated
                    next_pm_date = self._calculate_next_pm_date(
                        freq, self.get_first_installed_hist().date
                    )

                    if next_pm_date > active_rule.date:
                        next_pm_date = self._calculate_next_pm_date(
                            freq, active_rule.date, active_rule.freq.value
                        )
            else:
                # if no rule exists, origin will be the first installed location history date
                next_pm_date = self._calculate_next_pm_date(
                    freq, self.get_first_installed_hist().date
                )

            return Utility.datetime_to_str(next_pm_date)

        return None

    def location_free(self, pumps):
        last_location_self = self.get_actual_loc()
        if last_location_self is not None:
            for pump in pumps:
                last_location = pump.get_actual_loc()
                if (
                    last_location is not None
                    and last_location == last_location_self
                    and self.type == pump.type
                    and last_location_self.id != 1
                ):
                    return False
        return True

    def not_only_uninstalled(self):
        if len(self.lochistory) > 1:
            return True
        else:
            for lochistory in self.lochistory:
                if lochistory.loc.id == 1:
                    return False
        return True

    def get_active_rule(self, freq, rules):
        """
        Return the active rule for the pump instancea at a specific PM frequency.
        The active rule depends on :
            - pump id must mach self id
            - frequency of the related PM must match the specific passed frequency
              and the date of the rule must be greater than the date of today
              Or a synchro as been activated from an other PM

        """
        associated_rules = [
            rule
            for rule in rules
            if rule.pump.id == self.id
            and (rule.freq == freq and rule.date >= datetime.today())
        ]
        if len(associated_rules) > 0:
            return max(associated_rules)

        associated_rules = [
            rule for rule in rules if rule.pump.id == self.id and rule.synchro == True
        ]
        if len(associated_rules) > 0:
            return max(associated_rules)

        return None

    def get_associated_pm(self, pm, freq_id):
        """
        Return the PM that are linked to a specific PM frequency.
        Those have been automaticaly generated
        """
        return [
            associated_pm
            for associated_pm in self.pm
            if (
                associated_pm.freq.id in freq_id
                and associated_pm.date == pm.date
                and "Generated by" in associated_pm.com
            )
        ]

    def _get_last_hist(self):
        """Return the last location history"""
        if len(self.lochistory) > 0:
            return max(self.lochistory)

        return None

    def _get_last_pm(self, freq):
        """Return the last PM at specific frequency"""
        if len(self.pm) > 0:
            pms_at_freq = [pm for pm in self.pm if pm.freq == freq]
            if len(pms_at_freq) > 0:
                return next(
                    pm
                    for pm in pms_at_freq
                    if pm.date == max([pm.date for pm in pms_at_freq])
                )
        return None

    def _calculate_next_pm_date(self, freq, origin_date, rule_freq_period_diferrence=0):
        """
        Parameter:  freq : Frequency
                    origin_date : datetime
                    rule_freq_period_diferrence : int

        Calculate the date of the next PM to be done at specific frequency and with specific origin date.
        Generate all calculated PM since the origin
        List all realised PM
        Found the latest PM not yet done
        Apply the uninstalled period as per settings

        return datetime
        """
        calculated_passed_PM_dates = self._get_calculated_passed_PM_dates(
            origin_date, freq, rule_freq_period_diferrence
        )
        passed_PM_dates = self._get_passed_PM_dates(origin_date, freq)
        next_pm_date = self._match_calculated_and_real_pm(
            calculated_passed_PM_dates, passed_PM_dates, freq
        )
        next_pm_date += self._get_unactive_period(origin_date, datetime.today())

        return next_pm_date

    def _get_unactive_period(self, start, end):
        if continuous_installation_time == True:
            return relativedelta(days=0)
        else:
            sorted_hist = sorted([hist for hist in self.lochistory])
            uninstalled_hist = sorted(
                [
                    hist
                    for hist in sorted_hist
                    if hist.loc.value == 1 and start <= hist.date <= end
                ]
            )
            if len(uninstalled_hist) > 0:
                delta = 0
                for u_hist in uninstalled_hist:
                    next_hist = next(
                        (
                            [
                                hist
                                for hist in sorted_hist
                                if hist > u_hist and hist.loc.id != 1
                            ]
                        ),
                        None,
                    )
                    if next_hist is not None:
                        if next_hist.date > datetime.today():
                            pass
                        else:
                            delta += relativedelta(next_hist.date, u_hist.date)

                return delta
        return relativedelta(days=0)

    def _get_calculated_passed_PM_dates(
        self, date, freq, rule_freq_period_diferrence=0
    ):
        calculated_passed_pm = [date]
        next_pm_date = date + relativedelta(months=freq.value)
        if rule_freq_period_diferrence != 0:
            next_pm_date -= relativedelta(months=rule_freq_period_diferrence)
            calculated_passed_pm = [
                date - relativedelta(months=rule_freq_period_diferrence)
            ]

        while next_pm_date <= datetime.today():
            calculated_passed_pm.append(next_pm_date)
            next_pm_date += relativedelta(months=freq.value)

        return calculated_passed_pm

    def _get_passed_PM_dates(self, date, freq):
        return [
            pm.date
            for pm in self.pm
            if (pm.freq.id == freq.id and date <= pm.date <= datetime.today())
        ]

    def _match_calculated_and_real_pm(self, calculated_dates, real_dates, freq):
        calculated_dates.sort(key=lambda x: x, reverse=True)
        real_dates.sort(key=lambda x: x, reverse=True)
        for date in calculated_dates:
            if freq.value % 2 == 0:
                max_date = date + relativedelta(months=freq.value / 2)
                min_date = date - relativedelta(months=freq.value / 2)
            else:
                max_date = (
                    date
                    + relativedelta(months=int(freq.value / 2))
                    + relativedelta(days=15)
                )

                min_date = (
                    date
                    - relativedelta(months=int(freq.value / 2))
                    - relativedelta(days=15)
                )

            for real_date in real_dates:
                if min_date <= real_date <= max_date:
                    return date + relativedelta(months=freq.value)
        return calculated_dates[0] + relativedelta(months=freq.value)


class PM:
    def __init__(self, id, pump_id, freq, date, com, rule=None):
        """
        init expect
        """
        self.id = int(id)
        self.pump_id = int(pump_id)
        self.freq = freq
        self.date = Utility.str_to_datetime(date)
        self.com = com
        self.rule = rule

    def __eq__(self, obj):
        return self.date == obj.date and self.freq == obj.freq

    def __lt__(self, obj):
        return self.date < obj.date

    def dump(self):
        return {
            "id": self.id,
            "pump_id": self.pump_id,
            "freq_id": self.freq.id,
            "date": Utility.datetime_to_str(self.date),
            "com": self.com,
        }

    def exist(self, pms):
        for pm in pms:
            if pm == self:
                return pm
        return None


class LocHistory:
    def __init__(self, id, pump_id, loc, date):
        """
        init expect
        """
        self.id = int(id)
        self.pump_id = int(pump_id)
        self.loc = loc
        self.date = Utility.str_to_datetime(date)

    def __eq__(self, obj):
        return self.date == obj.date

    def __lt__(self, obj):
        return self.date < obj.date

    def dump(self):
        return {
            "id": self.id,
            "pump_id": self.pump_id,
            "loc_id": self.loc.id,
            "date": Utility.datetime_to_str(self.date),
        }

    def exist(self, hists):
        for hist in hists:
            if hist == self:
                return hist
        return None


class Frequency:
    def __init__(self, id, value):
        """
        init expect
        """
        self.id = int(id)
        self.value = value

    def __eq__(self, obj):
        return self.value == obj.value

    def __lt__(self, obj):
        return self.value < obj.value

    def dump(self):
        return {"id": self.id, "value": self.value}

    def exist(self, frequencies):
        for frequency in frequencies:
            if self == frequency:
                return frequency
        return None


class Location:
    def __init__(self, id, value):
        """
        init
        """
        self.id = int(id)
        self.value = value

    def __eq__(self, obj):
        return self.value == obj.value

    def __lt__(self, obj):
        return self.value < obj.value

    def dump(self):
        return {"id": self.id, "value": self.value}

    def exist(self, locations):
        for location in locations:
            if location == self:
                return location
        return None

    @staticmethod
    def get_id_from_value(value, locations):
        return next((loc.id for loc in locations if loc.value == value), None)


class Type:
    def __init__(self, id, value):
        """
        init expect
        """
        self.id = int(id)
        self.value = value

    def __eq__(self, obj):
        return self.value == obj.value

    def __lt__(self, obj):
        return self.value < obj.value

    def dump(self):
        return {"id": self.id, "value": self.value}

    def exist(self, types):
        for type in types:
            if type == self:
                return type
        return None

    @staticmethod
    def get_id_from_value(value, types):
        return next((type.id for type in types if type.value == value), None)


class Structure:
    def __init__(self, loc, type, freqs, freqs_id_associated):
        """
        init expect
        """
        self.loc = loc
        self.type = type
        self.freqs = freqs
        self.freqs_id_associated = freqs_id_associated

    def __eq__(self, other):
        if self is None or other is None:
            return False
        else:
            return (self.loc, self.type) == (other.loc, other.type)

    def __lt__(self, other):
        return (self.loc, self.type) < (other.loc, other.type)

    def freq_associated_id(self, freq_id):
        """
        Expect a frequency id (int)
        Return a list of frequency id (int)related to a specific frequency.
        """
        return next(
            (
                [int(id) for id in associated_freq["freq_id_associated"]]
                for associated_freq in self.freqs_id_associated
                if int(associated_freq["id"]) == freq_id
            ),
            [],
        )

    def dump(self):
        return {
            "loc_id": self.loc.id,
            "type_id": self.type.id,
            "freqs": [freq.id for freq in self.freqs],
        }

    def exist(self, structs):
        for struct in structs:
            if struct.loc.id == self.loc.id and struct.type.id == self.type.id:
                return struct
        return None


class Rules:
    def __init__(self, id, pump, freq, date, synchro):
        """
        init
        """
        self.id = id
        self.pump = pump
        self.freq = freq
        self.date = Utility.str_to_datetime(date)
        self.synchro = synchro

    def __eq__(self, obj):
        return self.pump == obj.pump and self.freq == obj.freq and self.date == obj.date

    def __lt__(self, other):
        return (self.date, self.freq, self.pump) < (other.date, other.freq, other.pump)

    def dump(self):
        return {
            "id": self.id,
            "pump_id": self.pump.id,
            "freq_id": self.freq.id,
            "date": Utility.datetime_to_str(self.date),
            "synchro": self.synchro,
        }


class Utility:
    @staticmethod
    def is_date(string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.

        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try:
            parse(string, fuzzy=fuzzy)
            return True

        except ValueError:
            return False

    @staticmethod
    def datetime_to_str(date):
        return datetime.strftime(date, "%Y/%m/%d")

    def str_to_datetime(string):
        return datetime.strptime(string, "%Y/%m/%d")

    def qdate_to_str(date):
        return date.toString("yyyy/MM/dd")


class Data:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.check_data_dir()
        datas = self.load_json()
        self.init(datas)

    def freq(self, id):
        return next(freq for freq in self.freqs if freq.id == id)

    def loc(self, id):
        loc = next((loc for loc in self.locs if loc.id == id), None)
        if loc is None:
            loc = next((loc for loc in self.locs if loc.value == id), None)
        return loc

    def type(self, id):
        return next(type for type in self.types if type.id == id)

    def pump(self, id):
        return next(pump for pump in self.pumps if pump.id == id)

    def check_data_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        if not os.path.exists("{0}location.json".format(self.data_dir)):
            open("{0}location.json".format(self.data_dir), "w").close()
        if not os.path.exists("{0}type.json".format(self.data_dir)):
            open("{0}type.json".format(self.data_dir), "w").close()
        if not os.path.exists("{0}frequency.json".format(self.data_dir)):
            open("{0}frequency.json".format(self.data_dir), "w").close()
        if not os.path.exists("{0}pm.json".format(self.data_dir)):
            open("{0}pm.json".format(self.data_dir), "w").close()
        if not os.path.exists("{0}history.json".format(self.data_dir)):
            open("{0}history.json".format(self.data_dir), "w").close()
        if not os.path.exists("{0}pump.json".format(self.data_dir)):
            open("{0}pump.json".format(self.data_dir), "w").close()
        if not os.path.exists("{0}structure.json".format(self.data_dir)):
            open("{0}structure.json".format(self.data_dir), "w").close()
        if not os.path.exists("{0}rules.json".format(self.data_dir)):
            open("{0}rules.json".format(self.data_dir), "w").close()

    def load_json(self):
        datas = {}
        with open("{0}location.json".format(self.data_dir), "r") as openfile:
            datas["location"] = json.load(openfile)
        with open("{0}type.json".format(self.data_dir), "r") as openfile:
            datas["type"] = json.load(openfile)
        with open("{0}frequency.json".format(self.data_dir), "r") as openfile:
            datas["frequency"] = json.load(openfile)
        with open("{0}pm.json".format(self.data_dir), "r") as openfile:
            datas["pm"] = json.load(openfile)
        with open("{0}history.json".format(self.data_dir), "r") as openfile:
            datas["history"] = json.load(openfile)
        with open("{0}pump.json".format(self.data_dir), "r") as openfile:
            datas["pumps"] = json.load(openfile)
        with open("{0}structure.json".format(self.data_dir), "r") as openfile:
            datas["structure"] = json.load(openfile)
        with open("{0}rules.json".format(self.data_dir), "r") as openfile:
            datas["rules"] = json.load(openfile)

        return datas

    def init(self, datas):
        self.freqs = [
            Frequency(freq["id"], freq["value"]) for freq in datas["frequency"]
        ]
        self.locs = [Location(loc["id"], loc["value"]) for loc in datas["location"]]
        self.types = [Type(type["id"], type["value"]) for type in datas["type"]]
        self.pm = [
            PM(
                pm["id"],
                pm["pump_id"],
                self.freq(int(pm["freq_id"])),
                pm["date"],
                pm["com"],
            )
            for pm in datas["pm"]
            if int(pm["pump_id"]) != 0
        ]
        self.history = [
            LocHistory(
                hist["id"],
                hist["pump_id"],
                self.loc(int(hist["loc_id"])),
                hist["date"],
            )
            for hist in datas["history"]
            if int(hist["pump_id"]) != 0
        ]
        self.struct = [
            Structure(
                self.loc(int(struct["loc_id"])),
                self.type(int(struct["type_id"])),
                [
                    self.freq(int(freq_id))
                    for freq_id in [freq_id["id"] for freq_id in struct["freqs"]]
                ],
                struct["freqs"],
            )
            for struct in datas["structure"]
        ]
        self.pumps = [
            Pump(
                pump["id"],
                self.type(int(pump["type_id"])),
                pump["serial"],
                [pm for pm in self.pm if int(pump["id"]) == pm.pump_id],
                (
                    [hist for hist in self.history if int(pump["id"]) == hist.pump_id],
                    self.struct,
                ),
            )
            for pump in datas["pumps"]
        ]
        self.rules = [
            Rules(
                rule["id"],
                self.pump(int(rule["pump_id"])),
                self.freq(int(rule["freq_id"])),
                rule["date"],
                bool(rule["synchro"]),
            )
            for rule in datas["rules"]
        ]

    def get_obj_by_attr(
        self, item_attribute, item_value, first_attribute, second_attribute=None
    ):
        """
        Return an item matching :
        - List = Data.first_attribute(.second_attribute)
        - Item = List.item_attribute == item_value
        """
        obj = getattr(self, first_attribute)
        if second_attribute is not None:
            obj = getattr(obj, second_attribute)

        return next(
            (item for item in obj if getattr(item, item_attribute) == item_value), None
        )

    def get_obj(self, item_value, first_attribute, second_attribute=None):
        obj = getattr(self, first_attribute)
        if second_attribute is not None:
            obj = getattr(obj, second_attribute)

        return next((item for item in obj if item == item_value), None)

    def get_new_id(self, attr):
        """
        Return a free id for a specific class List of Data.attr
        """
        list_item = getattr(self, attr)
        if len(list_item) > 0:
            list_id = [item.id for item in list_item]
            max_id = max(list_id)
            for i in range(2, max_id):
                if i not in list_id:
                    return i
            return max_id + 1
        else:
            return 1

    def save_location(self):
        location = json.dumps([o.dump() for o in self.locs], indent=3)

        with open("{0}location.json".format(self.data_dir), "w") as outfile:
            outfile.write(location)

    def save_frequency(self):
        frequency = json.dumps([o.dump() for o in self.freqs], indent=3)

        with open("{0}frequency.json".format(self.data_dir), "w") as outfile:
            outfile.write(frequency)

    def save_type(self):
        type = json.dumps([o.dump() for o in self.types], indent=3)

        with open("{0}type.json".format(self.data_dir), "w") as outfile:
            outfile.write(type)

    def save_structure(self):
        structure = json.dumps([o.dump() for o in self.struct], indent=3)

        with open("{0}structure.json".format(self.data_dir), "w") as outfile:
            outfile.write(structure)

    def save_pump(self):
        pumps = json.dumps([o.dump() for o in self.pumps], indent=3)

        with open("{0}pump.json".format(self.data_dir), "w") as outfile:
            outfile.write(pumps)

    def save_pm(self):
        pms = json.dumps([o.dump() for o in self.pm if o.pump_id != 0], indent=3)

        with open("{0}pm.json".format(self.data_dir), "w") as outfile:
            outfile.write(pms)

    def save_history(self):
        histories = json.dumps(
            [o.dump() for o in self.history if o.pump_id != 0], indent=3
        )

        with open("{0}history.json".format(self.data_dir), "w") as outfile:
            outfile.write(histories)

    def save_rules(self):
        rules = json.dumps([o.dump() for o in self.rules], indent=3)

        with open("{0}rules.json".format(self.data_dir), "w") as outfile:
            outfile.write(rules)
