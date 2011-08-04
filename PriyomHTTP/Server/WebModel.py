import xml.dom.minidom as dom
import time
import json
from datetime import datetime, timedelta
from libPriyom import Transmission, Station, Broadcast, Schedule

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
        
    def setCurrentFlags(self, flags):
        self.currentFlags = frozenset(flags)
        
    def setLimit(self, limit):
        self.limit = limit
        
    def setOffset(self, offset):
        self.offset = offset
    
    def setDistinct(self, distinct):
        self.distinct = distinct
    
    def exportToXml(self, obj, flags = None):
        if flags is None:
            flags = self.currentFlags
        return self.priyomInterface.exportToDom(obj, flags).toxml()
        
    def exportListToXml(self, list, classType, flags = None):
        if flags is None:
            flags = self.currentFlags
        return self.priyomInterface.exportListToDom(list, classType, flags).toxml()
        
    def limitResults(self, resultSet):
        resultSet.config(self.distinct, self.offset, self.limit)
        return resultSet
        
    def formatHTTPDate(self, dt):
        global weekdayname, monthname
        return dt.strftime("%%s, %d %%s %Y %T UTC") % (weekdayname[dt.weekday()], monthname[dt.month])
        
    def formatHTTPTimestamp(self, timestamp):
        return self.formatHTTPDate(datetime.fromtimestamp(timestamp))
        
    def now(self):
        return int(time.mktime(datetime.utcnow().timetuple()))
        
    def normalizeDate(self, dateTime):
        return datetime(year=dateTime.year, month=dateTime.month, day=dateTime.day)
        
    def toTimestamp(self, dateTime):
        return time.mktime(dateTime.timetuple())
        
    def importFromXml(self, doc, context = None, flags = None):
        context = context if context is not None else self.priyomInterface.getImportContext()
        for node in (node for node in doc.documentElement.childNodes if node.nodeType == dom.Node.ELEMENT_NODE):
            if node.tagName == "delete":
                try:
                    clsName = node.getAttribute("type")
                    id = node.getAttribute("id")
                except:
                    context.log("Something is wrong -- perhaps a missing attribute?")
                    continue
                try:
                    cls = {
                        "transmission": Transmission,
                        "broadcast": Broadcast,
                        "station": Station,
                        "schedule": Schedule
                    }[clsName]
                except KeyError:
                    context.log("Attempt to delete unknown type: %s" % node.getAttribute("type"))
                    continue
                try:
                    id = int(id)
                except ValueError:
                    context.log("Supplied invalid id to delete: %s" % node.getAttribute("id"))
                    continue
                obj = self.store.get(cls, id)
                if obj is None:
                    context.log("Cannot delete %s with id %d: Not found" % (str(cls), id))
                    continue
                if not self.priyomInterface.delete(obj, node.hasAttribute("force") and (node.getAttribute("force") == "true")):
                    context.log(u"Could not delete %s with id %d (did you check there are no more objects associated with it?)" % (unicode(cls), id))
                else:
                    context.log(u"Deleted %s with id %d" % (unicode(cls), id))
            else:
                try:
                    cls = {
                        "transmission": Transmission,
                        "broadcast": Broadcast,
                        "station": Station,
                        "schedule": Schedule
                    }[node.tagName]
                except KeyError:
                    context.log("Invalid transaction node: %s" % node.tagName)
                    continue
                context.importFromDomNode(node, cls)
        return context
        
    def importFromXmlStr(self, data, context = None, flags = None):
        doc = dom.parseString(data)
        return self.importFromXml(doc, context, flags)
        
    def importFromJson(self, tree, context = None, flags = None):
        raise Exception('JSON import not supported yet.')
        
    def importFromJsonStr(self, data, context = None, flags = None):
        tree = json.loads(data)
        return self.importFromJson(tree, context, flags)
