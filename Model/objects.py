import json
from datetime import datetime

class Pump:

    def __init__(self, id, type, serial, pms, lochistory):
        """
        init expect : pump type, 
        """
        self.id = str(id)
        self.type = type
        self.serial = serial
        self.pm = pms
        self.lochistory = lochistory

    def __eq__(self, other):
        return self.serial.lower() == other.serial.lower()

    def dump(self):
        return {'id': self.id,
                'type_id': self.type.id,
                'serial': self.serial,
                'pm' : [o.dump() for o in self.pm],
                'lochistory' : [o.dump() for o in self.lochistory]
                }

    def exist(self, pumps):
        for pump in pumps:
            if pump == self:
                return pump
        return None
    
    def get_actual_loc(self):
        if len(self.lochistory) > 0:
            lastlocdate = max([datetime(hist.date.year, hist.date.month, hist.date.day) for hist in self.lochistory])
            lastloc = next((hist.loc for hist in self.lochistory if datetime(hist.date.year, hist.date.month, hist.date.day) == lastlocdate), None)           
            return lastloc
        return None
    
    def get_previous_loc(self):
        previouslocid = None
        if len(self.lochistory) > 1:
            datelistesorted = sorted([datetime(hist.date.year, hist.date.month, hist.date.day) for hist in self.lochistory])
            previouslocdate = datelistesorted[-2]
            previouslocid = next((hist.loc.id for hist in self.lochistory if datetime(hist.date.year, hist.date.month, hist.date.day) == previouslocdate), None)           
        return previouslocid

    def get_last_pm_date(self, freq_id):
        lastpm = None
        if len(self.pm) > 0:
            pms_at_freq = [pm for pm in self.pm if pm.freq.id == freq_id]
            if len(pms_at_freq) > 0:
                lastpm = datetime.strftime(max([pm.date for pm in pms_at_freq]), '%Y/%m/%d')
        return lastpm
 
    def location_free(self, pumps):
        free = True
        last_location_self = self.get_actual_loc()
        if last_location_self is not None:
            for pump in pumps:
                last_location = pump.get_actual_loc()
                if last_location is not None and last_location == last_location_self and self.type == pump.type:
                    free = False
                    break
        return free

    def not_only_uninstalled(self):
        if len(self.lochistory) > 1:
            return True
        else:
             for lochistory in self.lochistory:
                if lochistory.loc.id == "1":
                    return False
        return True

class PM: 

    def __init__(self, freq, date, com):
        """
        init expect 
        """
        self.freq = freq
        self.date = datetime.strptime(date, '%Y/%m/%d')
        self.com = com

    def __eq__(self, obj):
        return (self.date == obj.date and self.freq == obj.freq)

    def __lt__(self, obj):
        return self.date < obj.date

    def get_date_to_string(self):
        return self.date.strftime('%Y/%m/%d')

    def dump(self):
        return {'freq_id': self.freq.id,
                'date': datetime.strftime(self.date, '%Y/%m/%d'),
                'com' : self.com
                }

    def exist(self, pms):
        for pm in pms:
            if pm == self:
                return pm
        return None

class LocHistory: 
    def __init__(self, loc, date):
        """
        init expect 
        """
        self.loc = loc
        self.date = datetime.strptime(date, '%Y/%m/%d')

    def __eq__(self, obj):
        return (self.date == obj.date and self.loc == obj.loc)

    def __lt__(self, obj):
        return self.date < obj.date

    def get_date_to_string(self):
        return self.date.strftime('%Y/%m/%d')

    def dump(self):
        return {'loc_id': self.loc.id,
                'date': datetime.strftime(self.date, '%Y/%m/%d')
                }

    def exist(self, hists):
        for hist in hists:
            if hist == self:
                return hist
        return None

class Frequency: 

    def __init__(self, freq_id, value):
        """
        init expect
        """
        self.id = str(freq_id)
        self.value = str(value)

    def __eq__(self, obj):
        return (int(self.value) == int(obj.value))

    def __lt__(self, obj):
        return int(self.value) < int(obj.value)

    def dump(self):
        return {'id': self.id,
                'value': self.value}

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
        self.id = str(id)
        self.value = value

    def __eq__(self, obj):
        return (self.value == obj.value)

    def __lt__(self, obj):
        return self.value < obj.value

    def dump(self):
        return {'id': self.id,
                'value' : self.value
                }

    def exist(self,locations):
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
        self.id = id
        self.value = value
    
    def __eq__(self, obj):
        return (self.value == obj.value)

    def __lt__(self, obj):
        return self.value < obj.value

    def dump(self):
        return {'id': self.id,
                'value' : self.value
                }

    def exist(self, types):
        for type in types:
            if type == self:
                return type
        return None

    @staticmethod
    def get_id_from_value(value, types):
        return next((type.id for type in types if type.value == value), None)

class PMStructure: 

    def __init__(self, loc, type, freqs):
        """
        init expect
        """
        self.loc = loc
        self.type = type
        self.freqs = freqs

    def __eq__(self, other):
        return (self.loc, self.type) == (other.loc, other.type)

    def __lt__(self, other):
        return (self.loc, self.type) < (other.loc, other.type)

    def loc_in_struct(self, loc):
        return loc == self.loc
        
    def dump(self):
        return {'loc_id': self.loc.id,
                'type_id': self.type.id,
                'freqs' : [freq.id for freq in self.freqs]
                }

    def exist(self, structs):
        for struct in structs:
            if struct.loc.id == self.loc.id and struct.type.id == self.type.id:
                return struct
        return None

class Rules:
    def __init__(self, struct_from, struct_to, freq, next_pm, dir):
        """
        init
        """
        self.struct_from = struct_from
        self.struct_to = struct_to
        self.freq = freq
        self.next_pm = next_pm
        self.dir = dir
    
    def __eq__(self, obj):
        return (self.struct_from == obj.struct_from and 
                self.struct_to == obj.struct_to and
                self.freq == obj.freq)
        
    def dump(self):
        return {'loc_id_from': self.struct_from.loc.id,
                'type_id_from' : self.struct_from.type.id,
                'loc_id_to': self.struct_to.loc.id,
                'type_id_to' : self.struct_to.type.id,
                'freq_id': self.freq.id,
                'next_pm' : self.next_pm,
                'dir' : self.dir
                }

    def exist(self, rules):
        for rule in rules:
            if rule == self:
                return rule
        return None

class Data:
    def __init__(self):
        datas = self.load_data()
        self.freqs = [Frequency(freq["id"], freq["value"]) for freq in datas["frequency"]]
        self.locs = [Location(loc["id"], loc["value"]) for loc in datas["location"]]
        self.types = [Type(type["id"], type["value"]) for type in datas["type"]]

        self.struct = [
            PMStructure(
                next(loc for loc in self.locs if loc.id == struct["loc_id"]),
                next(type for type in self.types if type.id == struct["type_id"]),
                [next(freq for freq in self.freqs if freq.id == freq_id) for freq_id in struct["freqs"]]
            ) for struct in datas["structure"]]
        self.pumps = [
            Pump(
                pump["id"],
                next(type for type in self.types if type.id == pump["type_id"]),
                pump["serial"],
                [
                    PM(
                        next(freq for freq in self.freqs if freq.id == pm["freq_id"]),
                        pm["date"],
                        pm["com"]
                    ) for pm in pump["pm"]],
                [
                    LocHistory(
                        next(loc for loc in self.locs if loc.id == hist["loc_id"]),
                        hist["date"]
                    ) for hist in pump["lochistory"]]
            )
            for pump in datas["pumps"]
        ]
        self.rules = [
            Rules(
                next(struct for struct in self.struct if (struct.loc.id == rule["loc_id_from"] and struct.type.id == rule["type_id_from"])),
                next(struct for struct in self.struct if (struct.loc.id == rule["loc_id_to"] and struct.type.id == rule["type_id_to"])),
                next(freq for freq in self.freqs if freq.id == rule["freq_id"]),
                rule["next_pm"],
                rule["dir"]
            )
            for rule in datas["rules"]]

    def load_data(self):
        datas = {}
        with open('Data/location.json', 'r') as openfile:
           datas["location"] = json.load(openfile)
        with open('Data/type.json', 'r') as openfile:
           datas["type"] = json.load(openfile)
        with open('Data/frequency.json', 'r') as openfile:
           datas["frequency"] = json.load(openfile)
        with open('Data/pump.json', 'r') as openfile:
           datas["pumps"] = json.load(openfile)
        with open('Data/structure.json', 'r') as openfile:
           datas["structure"] = json.load(openfile)
        with open('Data/rules.json', 'r') as openfile:
           datas["rules"] = json.load(openfile)
        
        return datas
    
    def get_obj_by_attr(self, item_attribute, item_value, first_attribute, second_attribute = None):
        obj = getattr(self, first_attribute)        
        if second_attribute is not None:
            obj = getattr(obj, second_attribute)
        
        return next((item for item in obj if getattr(item, item_attribute) == item_value), None) 

    def get_obj(self, item_value, first_attribute, second_attribute = None):
        obj = getattr(self, first_attribute)        
        if second_attribute is not None:
            obj = getattr(obj, second_attribute)
        
        return next((item for item in obj if item == item_value), None) 

    def save_location(self):
        location = json.dumps([o.dump() for o in self.locs], indent=3)
        
        with open("Data/location.json", "w") as outfile:
            outfile.write(location)

    def save_frequency(self):
        frequency = json.dumps([o.dump() for o in self.freqs], indent=3)

        with open("Data/frequency.json", "w") as outfile:
            outfile.write(frequency)

    def save_type(self):
        type = json.dumps([o.dump() for o in self.types], indent=3)

        with open("Data/type.json", "w") as outfile:
            outfile.write(type)

    def save_structure(self):
        structure = json.dumps([o.dump() for o in self.struct], indent=3)
        
        with open("Data/structure.json", "w") as outfile:
            outfile.write(structure)

    def save_pump(self):
        pumps = json.dumps([o.dump() for o in self.pumps], indent=3)
        
        with open("Data/pump.json", "w") as outfile:
            outfile.write(pumps)

    def save_rules(self):
        rules = json.dumps([o.dump() for o in self.rules], indent=3)
        
        with open("Data/rules.json", "w") as outfile:
            outfile.write(rules)