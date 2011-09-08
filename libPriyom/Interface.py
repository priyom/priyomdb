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
        Broadcast: "priyom-broadcast-export",
        TransmissionClass: "priyom-generic-export",
        TransmissionClassTable: "priyom-generic-export"
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
        """return {
            Transmission: self.exportTransmissionToDom,
            Schedule: self.exportScheduleToDom,
            Station: self.exportStationToDom,
            Broadcast: self.exportBroadcastToDom,
            TransmissionClass: self.exportTrans
        }[type(obj)](obj, flags, doc)"""
        return self._exportToDomSimple(obj, self.Class2RootNode[type(obj)], flags, doc)
        
    def exportListToDom(self, list, classType, flags = None, doc = None):
        doc = self._getClassDoc(classType, doc)
        for obj in list:
            obj.toDom(doc.documentElement, flags)
        return doc
        
    def getImportContext(self):
        return Imports.ImportContext(self.store)
        
    def deleteTransmissionBlock(self, obj, force = False):
        store = self.store
        obj.deleteForeignSupplements()
        store.remove(obj)
        
    def deleteTransmission(self, obj, force = False):
        store = self.store
        blocks = obj.blocks
        for block in blocks:
            self.deleteTransmissionBlock(block, True)
        if obj.ForeignCallsign is not None:
            Store.of(obj.ForeignCallsign.supplement).remove(obj.ForeignCallsign.supplement)
        store.remove(obj)
        return True
        
    def deleteScheduleLeaf(self, obj, force = False):
        store = self.store
        freqs = store.find(ScheduleLeafFrequency, ScheduleLeafFrequency.ScheduleLeafID == obj.ID)
        if force:
            freqs.remove()
        else:
            if freqs.count() > 0:
                return False
        store.remove(obj)
        return True
        
    def deleteSchedule(self, obj, force = False):
        store = self.store
        stations = store.find(Station, Station.ScheduleID == obj.ID)
        # won't delete all stations which are using this schedule, not
        # even with force == True
        if stations.count() > 0:
            return False
        children = store.find(Schedule, Schedule.ParentID == obj.ID)
        leaves = store.find(ScheduleLeaf, ScheduleLeaf.ScheduleID == obj.ID)
        if force:
            for child in children:
                self.deleteSchedule(child, True)
            for leaf in leaves:
                self.deleteScheduleLeaf(leaf, True)
        else:
            if children.count() > 0:
                return False
            if leaves.count() > 0:
                return False
        store.remove(Schedule)
        return True
    
    def deleteStation(self, obj, force = False):
        store = self.store
        broadcasts = store.find(Broadcast, Broadcast.StationID == obj.ID)
        if force:
            for broadcast in broadcasts:
                self.deleteBroadcast(broadcast, True)
        else:
            if broadcasts.count() > 0:
                return False
        store.remove(obj)
        return True
        
    def deleteBroadcast(self, obj, force = False):
        store = self.store
        transmissions = store.find(Transmission, Transmission.BroadcastID == obj.ID)
        if force:
            for transmission in transmissions:
                self.deleteTransmission(transmission, True)
        else:
            if transmissions.count() > 0:
                return False
        store.find(BroadcastFrequency, BroadcastFrequency.BroadcastID == obj.ID).remove()
        store.remove(obj)
        return True
        
    def delete(self, obj, force = False):
        try:
            method = {
                Transmission: self.deleteTransmission,
                Schedule: self.deleteSchedule,
                Station: self.deleteStation,
                Broadcast: self.deleteBroadcast
            }[type(obj)]
        except KeyError:
            raise Exception("Can only delete elementary objects (got object of type %s)." % (str(type(obj))))
        return method(obj, force)
        
    def importTransaction(self, doc):
        context = self.getImportContext()
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
                if not self.delete(obj, node.hasAttribute("force") and (node.getAttribute("force") == "true")):
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
        
    def getStation(self, stationDesignator, head = False):
        try:
            stationId = int(stationDesignator)
        except ValueError:
            stationId = None
        if stationId is not None:
            station = self.store.get(Station, stationId)
        else:
            resultSet = self.store.find(Station, Station.EnigmaIdentifier == stationDesignator)
            station = resultSet.any()
            if station is None:
                resultSet = self.store.find(Station, Station.PriyomIdentifier == stationDesignator)
            station = resultSet.any()
        return (station.Modified, station)
        
    def getCloseBroadcasts(self, stationId, time, jitter, head = False):
        wideBroadcasts = self.store.find(Broadcast, Broadcast.StationID == stationId)
        lastModified = wideBroadcasts.max(Broadcast.Modified)
        if head:
            return (lastModified, None)
        
        broadcasts = wideBroadcasts.find(And(
            Broadcast.BroadcastStart <= time + jitter,
            Broadcast.BroadcastEnd > time - jitter
        ))
        return (lastModified, broadcasts)
        
    def listObjects(self, cls, limiter = None, head = False):
        objects = self.store.find(cls)
        if limiter is not None:
            objects = limiter(objects)
        lastModified = objects.max(cls.Modified)
        if head:
            return (lastModified, None)
        return (lastModified, objects)
