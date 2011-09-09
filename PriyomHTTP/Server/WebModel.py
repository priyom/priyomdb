from storm.locals import AutoReload
import xml.dom.minidom as dom
import time
import json
from datetime import datetime, timedelta
from libPriyom import Transmission, Station, Broadcast, Schedule
from APIDatabase import Variable

weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
monthname = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

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
        self.lastReset = self.now()
        
    def getLastUpdate(self):
        return self.varLastUpdate.Value
    
    def exportToXml(self, obj, flags = None):
        if flags is None:
            flags = self.currentFlags
        return self.priyomInterface.exportToDom(obj, flags).toxml()
        
    def exportListToXml(self, list, classType, flags = None):
        if flags is None:
            flags = self.currentFlags
        return self.priyomInterface.exportListToDom(list, classType, flags).toxml()
        
    def getExportDoc(self, rootNodeName):
        return self.priyomInterface.createDocument(rootNodeName)
        
    def limitResults(self, resultSet):
        resultSet.config(self.distinct, self.offset, self.limit)
        return resultSet
        
    def formatHTTPDate(self, dt):
        global weekdayname, monthname
        return dt.strftime("%%s, %d %%s %Y %T UTC") % (weekdayname[dt.weekday()], monthname[dt.month])
        
    def formatHTTPTimestamp(self, timestamp):
        return self.formatHTTPDate(datetime.fromtimestamp(timestamp))
        
    def now(self):
        return self.priyomInterface.now()
        
    def importFromXml(self, doc, context = None, flags = None):
        context = self.priyomInterface.importTransaction(doc)
        self.varLastUpdate.Value = unicode(self.now())
        self.store.commit()
        self.resetStore()
        return context
        
    def importFromXmlStr(self, data, context = None, flags = None):
        doc = dom.parseString(data)
        return self.importFromXml(doc, context, flags)
        
    def importFromJson(self, tree, context = None, flags = None):
        raise Exception('JSON import not supported yet.')
        
    def importFromJsonStr(self, data, context = None, flags = None):
        tree = json.loads(data)
        return self.importFromJson(tree, context, flags)
