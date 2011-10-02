"""
File name: WebModel.py
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
from storm.locals import AutoReload
import xml.etree.ElementTree as ElementTree
import time
from datetime import datetime, timedelta
from libPriyom import Transmission, Station, Broadcast, Schedule, TimeUtils
from APIDatabase import Variable
import re
import cStringIO
import io
from cfg_priyomhttpd import application, misc

weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
monthname = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
monthname_to_idx = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12
}
rfc1123 = {
    "expression": re.compile("[A-Za-z]{3},\s+([0-9]{2})\s+([A-Za-z]{3})\s+([0-9]{4})\s+([0-9]{2}:[0-9]{2}:[0-9]{2})\s+GMT"),
    "year": 2,
    "month": 1,
    "day": 0,
    "time": 3,
    "yearmode": "%Y"
}
rfc850 = {
    "expression": re.compile("[A-Za-z]+,\s+([0-9]{2})-([A-Za-z]{3})-([0-9]{2})\s+([0-9]{2}:[0-9]{2}:[0-9]{2})\s+GMT"),
    "year": 2,
    "month": 1,
    "day": 0,
    "time": 3,
    "yearmode": "%y"
}
asctime = {
    "expression": re.compile("[A-Za-z]{3}\s+([A-Za-z]{3})\s+([0-9]{1,2})\s+([0-9]{2}:[0-9]{2}:[0-9]{2})\s+([0-9]{4})"),
    "year": 3,
    "month": 0,
    "day": 1,
    "time": 2,
    "yearmode": "%Y"
}
class Encoder(io.IOBase):
    def __init__(self, targetEncoding):
        self.buffer = cStringIO.StringIO()
        self.targetEncoding = targetEncoding
        
    def write(self, buf):
        self.buffer.write(buf.encode(self.targetEncoding, errors='xmlcharrefreplace'))
        
    def getvalue(self):
        return self.buffer.getvalue()
    
    def close(self):
        self.buffer.close()

class WebModel(object):
    def __init__(self, priyomInterface):
        self.priyomInterface = priyomInterface
        self.store = self.priyomInterface.store
        self.currentFlags = None
        self.limit = None
        self.offset = None
        self.distinct = False
        self.resetStore()
        
    def setCurrentFlags(self, flags):
        self.currentFlags = frozenset(flags)
        
    def setLimit(self, limit):
        self.limit = limit
        
    def setOffset(self, offset):
        self.offset = offset
    
    def setDistinct(self, distinct):
        self.distinct = distinct
        
    def __call__(self, query):
        return self.limitResults(query)
        
    def getVarLastUpdate(self):
        if self.varLastUpdate is None:
            self.varLastUpdate = self.store.get(Variable, u"lastImport")
        return self.varLastUpdate
        
    def checkReset(self):
        if self.varLastUpdate is None:
            self.varLastUpdate = self.store.get(Variable, u"lastImport")
        if self.varLastUpdate is not None:
            self.varLastUpdate.Value = AutoReload
            if self.varLastUpdate.Value is not None:
                if self.lastReset < int(self.varLastUpdate.Value):
                    self.resetStore()
                    
    def resetStore(self):
        self.store.reset()
        self.varLastUpdate = self.store.get(Variable, u"lastImport")
        self.lastReset = int(TimeUtils.now())
        
    def getLastUpdate(self):
        self.getVarLastUpdate()
        if self.varLastUpdate is None:
            return int(TimeUtils.now())
        return self.varLastUpdate.Value
        
    def etreeToFile(self, file, etree, encoding="UTF-8"):
        etree.write(file, encoding=encoding, xml_declaration=True, method="xml")
        
    def exportToETree(self, obj, flags = None):
        if flags is None:
            flags = self.currentFlags
        return self.priyomInterface.exportToETree(obj, flags)
    
    def exportToFile(self, obj, flags = None, encoding=None):
        self.etreeToFile(file, self.exportToETree(obj, flags=flags), encoding=encoding)
        
    def exportListToETree(self, list, classType, flags = None):
        if flags is None:
            flags = self.currentFlags
        return self.priyomInterface.exportListToETree(list, classType, flags)
    
    def exportListToFile(self, file, list, classType, flags=None, encoding=None):
        self.etreeToFile(file, self.exportListToETree(list, classType, flags), encoding=encoding)
        
    def getExportTree(self, rootNodeName):
        return self.priyomInterface.createDocument(rootNodeName)
        
    def limitResults(self, resultSet):
        resultSet.config(self.distinct, self.offset, self.limit)
        return resultSet
        
    def formatHTTPDate(self, dt):
        global weekdayname, monthname
        return dt.strftime("%%s, %d %%s %Y %T GMT") % (weekdayname[dt.weekday()], monthname[dt.month])
        
    def formatHTTPTimestamp(self, timestamp):
        return self.formatHTTPDate(TimeUtils.toDatetime(timestamp))
        
    def parseHTTPDate(self, httpDate):
        global rfc1123, rfc850, asctime, monthname_to_idx
        standard = rfc1123
        match = standard["expression"].match(httpDate)
        if match is None:
            standard = rfc850
            match = standard["expression"].match(httpDate)
        if match is None:
            standard = asctime
            match = standard["expression"].match(httpDate)
        if match is None:
            raise ValueError("%r does not match any standard (rfc1123, rfc850 and asctime supported)." % (httpDate))
        
        groups = match.groups()
        year = groups[standard["year"]]
        try:
            month = monthname_to_idx[groups[standard["month"]]]
        except KeyError:
            return None
        day = groups[standard["day"]]
        time = groups[standard["time"]]
        
        return datetime.strptime("%s %d %s %s" % (year, month, day, time), "%s %%m %%d %%H:%%M:%%S" % (standard["yearmode"]))
    
    def parseHTTPTimestamp(self, httpDate):
        return TimeUtils.toTimestamp(self.parseHTTPDate(httpDate))
        
    def importFromETree(self, tree, context = None, flags = None):
        context = self.priyomInterface.importTransaction(tree)
        self.varLastUpdate.Value = unicode(int(TimeUtils.now()))
        self.store.commit()
        self.resetStore()
        return context
        
    def importFromXmlStr(self, data, context = None, flags = None):
        tree = ElementTree.XML(data)
        return self.importFromETree(tree, context, flags)
        
    def formatHTMLTitle(self, pageTitle, appNameSuffix = u""):
        return u"""{0}{1}{2}""".format(
            pageTitle,
            (misc.get("titleSeparator", u" ") + application["name"] + appNameSuffix) if "name" in application else u"",
            (misc.get("titleSeparator", u" ") + application["host"]) if "host" in application else u""
        )
        
    def rootPath(self, rootPath):
        if len(rootPath) > 0 and rootPath[0] != u"/":
            return application.get("urlroot", u"") + u"/" + rootPath
        else:
            return application.get("urlroot", u"") + rootPath
