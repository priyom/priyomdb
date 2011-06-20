from storm.locals import *
import imports
import xmlintf
import xml.dom.minidom as dom
from modulations import Modulation
from broadcasts import BroadcastFrequency, Broadcast
from transmissions import Transmission, TransmissionClass, TransmissionClassTable, TransmissionClassTableField
from schedules import Schedule, ScheduleLeaf
from stations import Station
from foreign import ForeignSupplement
from helpers.scheduleMaintainer import ScheduleMaintainer

class NoPriyomInterfaceError(Exception):
    def __init__(self):
        super(NoPriyomInterfaceError, self).__init__("No priyom interface defined.")

class PriyomInterface:
    def __init__(self, store):
        if store is None:
            raise ValueError("store must not be None.")
        self.store = store
        self.scheduleMaintainer = ScheduleMaintainer(store)
        
    def createDocument(self, rootNodeName):
        return dom.getDOMImplementation().createDocument(xmlintf.namespace, rootNodeName, None)
        
    def _createDocumentOptional(self, givendoc, rootNodeName):
        return self.createDocument(rootNodeName) if givendoc is None else givendoc
        
    def _exportToDomSimple(self, obj, rootName, flags = None, doc = None):
        thisDoc = self._createDocumentOptional(doc, rootName)
        obj.toDom(thisDoc.documentElement, flags)
        return thisDoc
        
    def exportTransmissionToDom(self, transmission, flags = None, doc = None):
        return self._exportToDomSimple(transmission, "priyom-transmission-export", flags, doc)
        
    def exportScheduleToDom(self, transmission, flags = None, doc = None):
        return self._exportToDomSimple(transmission, "priyom-schedule-export", flags, doc)
        
    def exportStationToDom(self, transmission, flags = None, doc = None):
        return self._exportToDomSimple(transmission, "priyom-station-export", flags, doc)
        
    def exportBroadcastToDom(self, transmission, flags = None, doc = None):
        return self._exportToDomSimple(transmission, "priyom-broadcast-export", flags, doc)
        
    def exportToDom(self, obj, flags = None, doc = None):
        return {
            Transmission: self.exportTransmissionToDom,
            Schedule: self.exportScheduleToDom,
            Station: self.exportStationToDom,
            Broadcast: self.exportBroadcastToDom
        }[type(obj)](obj, flags, doc)
        
    def _importFromDomSimple(self, cls, node):
        imports.importSimple(self.store, cls, node)
        
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
