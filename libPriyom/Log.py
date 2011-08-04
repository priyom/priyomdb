import datetime
import Formatting

class LogEntry(object):
    def __init__(self, obj, facility):
        self.timestamp = datetime.datetime.utcnow()
        if type(obj) == str:
            obj = obj.decode("utf-8")
        self.message = unicode(obj)
        self.facility = facility
        
    def format(self, format):
        return format.replace("%t", self.timestamp.strftime(Formatting.priyomdate))
            .replace("%f", self.facility)
            .replace("%m", self.message)

class LogFacility(object):
    def __init__(self, name):
        self.name = name
        self.buffer = []
        self.flushFormat = "[%t] [%f] %m"
        
    def log(self, obj):
        entry = LogEntry(obj, self)
        self.buffer.append(entry)
        return entry
        
    def get(self):
        return "\n".join((entry.format(self.flushFormat) for entry in self.buffer))
        
    def flush(self):
        data = self.get()
        self.buffer = []
        return data

class Log(object):
    def __init__(self, facilities, defaultFacility):
        self.facilities = {}
        for facility in facilities:
            self.facilities[facility] = LogFacility()
        self.defaultFacility = self.facilities[defaultFacility]
        self.format = "[%t] [%f] %m"
        self.buffer = []
        
    def log(self, obj, facility = None):
        if facility is None:
            entry = self.defaultFacility.log(obj)
        else:
            entry = self.facilities[facility].log(obj)
        self.buffer.append(entry)
            
    def get(self):
        return "\n".join((entry.format(self.format) for entry in self.buffer))
