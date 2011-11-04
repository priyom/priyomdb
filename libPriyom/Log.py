"""
File name: Log.py
This file is part of: priyomdb

LICENSE

The contents of this file are subject to the Mozilla Public License
Version 1.1 (the "License"); you may not use this file except in
compliance with the License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/

Software distributed under the License is distributed on an "AS IS"
basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
License for the specific language governing rights and limitations under
the License.

Alternatively, the contents of this file may be used under the terms of
the GNU General Public license (the  "GPL License"), in which case  the
provisions of GPL License are applicable instead of those above.

FEEDBACK & QUESTIONS

For feedback and questions about priyomdb please e-mail one of the
authors:
    Jonas Wielicki <j.wielicki@sotecware.net>
"""
import datetime
import libPriyom.Formatting as Formatting

class LogEntry(object):
    def __init__(self, obj, facility):
        self.timestamp = datetime.datetime.utcnow()
        if type(obj) == str:
            obj = obj.decode("utf-8")
        self.message = unicode(obj)
        self.facility = facility
        
    def format(self, format):
        return format.replace("%t", self.timestamp.strftime(Formatting.priyomdate)).replace("%f", self.facility.name).replace("%m", self.message)

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
            self.facilities[facility] = LogFacility(facility)
        self.defaultFacility = self.facilities[defaultFacility]
        self.format = "[%t] [%f] %m"
        self.buffer = []
        
    def log(self, obj, facility = None):
        if facility is None:
            entry = self.defaultFacility.log(obj)
        else:
            entry = self.facilities[facility].log(obj)
        self.buffer.append(entry)
        
    def __call__(self, obj, facility = None):
        self.log(obj, facility)
        
    def get(self):
        return "\n".join((entry.format(self.format) for entry in self.buffer))
