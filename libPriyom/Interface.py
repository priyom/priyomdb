from storm.locals import *
import Imports
import XMLIntf
import xml.dom.minidom as dom
from Modulation import Modulation
from Broadcast import BroadcastFrequency, Broadcast
from Transmission import Transmission, TransmissionClass, TransmissionClassTable, TransmissionClassTableField
from Schedule import Schedule, ScheduleLeaf
from Station import Station
from Foreign import ForeignSupplement
from Helpers.ScheduleMaintainer import ScheduleMaintainer

class NoPriyomInterfaceError(Exception):
    def __init__(self):
        super(NoPriyomInterfaceError, self).__init__("No priyom interface defined.")

class PriyomInterface:
    Class2RootNode = {
        Transmission: "priyom-transmission-export",
        Schedule: "priyom-schedule-export",
        Station: "priyom-station-export",
        Broadcast: "priyom-broadcast-export"
    }
    
    def __init__(self, store):
        if store is None:
            raise ValueError("store must not be None.")
        self.store = store
        self.scheduleMaintainer = ScheduleMaintainer(store)
        
    def createDocument(self, rootNodeName):
        return dom.getDOMImplementation().createDocument(XMLIntf.namespace, rootNodeName, None)
        
    def _createDocumentOptional(self, givendoc, rootNodeName):
        return self.createDocument(rootNodeName) if givendoc is None else givendoc
        
    def _getClassDoc(self, classType, doc):
        return self._createDocumentOptional(doc, self.Class2RootNode[classType])
        
    def _exportToDomSimple(self, obj, rootName, flags = None, doc = None):
        thisDoc = self._getClassDoc(type(obj), doc)
        obj.toDom(thisDoc.documentElement, flags)
        return thisDoc
        
    def exportTransmissionToDom(self, transmission, flags = None, doc = None):
        return self._exportToDomSimple(transmission, "priyom-transmission-export", flags, doc)
        
    def exportScheduleToDom(self, schedule, flags = None, doc = None):
        return self._exportToDomSimple(schedule, "priyom-schedule-export", flags, doc)
        
    def exportStationToDom(self, station, flags = None, doc = None):
        return self._exportToDomSimple(station, "priyom-station-export", flags, doc)
        
    def exportBroadcastToDom(self, broadcast, flags = None, doc = None):
        return self._exportToDomSimple(broadcast, "priyom-broadcast-export", flags, doc)
        
    def exportToDom(self, obj, flags = None, doc = None):
        return {
            Transmission: self.exportTransmissionToDom,
            Schedule: self.exportScheduleToDom,
            Station: self.exportStationToDom,
            Broadcast: self.exportBroadcastToDom
        }[type(obj)](obj, flags, doc)
        
    def exportListToDom(self, list, classType, flags = None, doc = None):
        doc = self._getClassDoc(classType, doc)
        for obj in list:
            obj.toDom(doc.documentElement, flags)
        return doc
        
    def _importFromDomSimple(self, cls, node):
        Imports.importSimple(self.store, cls, node)
        
    def importTransmissionFromDom(self, node):
        return self._importFromDomSimple(Transmission, node)
        
    def importStationFromDom(self, node):
        return self._importFromDomSimple(Station, node)
        
    def importScheduleFromDom(self, node):
        return self._importFromDomSimple(Schedule, node)
        
    def importBroadcastFromDom(self, node):
        return self._importFromDomSimple(Broadcast, node)
        
    def importFromDom(self, node):
        return {
            "transmission": self.importTransmissionFromDom,
            "schedule": self.importScheduleFromDom,
            "station": self.importStationFromDom,
            "broadcast": self.importBroadcastFromDom
        }[node.tagName](node)
