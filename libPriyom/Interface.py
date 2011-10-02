"""
File name: Interface.py
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
from storm.locals import *
from storm.expr import *
import Imports
import XMLIntf
from xml.etree.ElementTree import ElementTree
from Modulation import Modulation
from Broadcast import BroadcastFrequency, Broadcast
from Transmission import Transmission, TransmissionClass, TransmissionClassTable, TransmissionClassTableField
from Schedule import Schedule, ScheduleLeaf
from Station import Station
from Foreign import ForeignSupplement
from Helpers.ScheduleMaintainer import ScheduleMaintainer
import time
from datetime import datetime, timedelta
from Helpers import TimeUtils

PAST = u"past"
ONAIR = u"on-air"
UPCOMING = u"upcoming"

def longOrNone(s):
    try:
        return long(s)
    except:
        return None

class NoPriyomInterfaceError(Exception):
    def __init__(self):
        super(NoPriyomInterfaceError, self).__init__("No priyom interface defined.")

class PriyomInterface:
    Class2RootNode = {
        Transmission: u"priyom-transmission-export",
        Schedule: u"priyom-schedule-export",
        Station: u"priyom-station-export",
        Broadcast: u"priyom-broadcast-export",
        TransmissionClass: u"priyom-generic-export",
        TransmissionClassTable: u"priyom-generic-export"
    }
    
    def __init__(self, store):
        if store is None:
            raise ValueError("store must not be None.")
        self.store = store
        self.scheduleMaintainer = ScheduleMaintainer(self)
        
    def createDocument(self, rootNodeName):
        return ElementTree.ElementTree(ElementTree.Element(u"{{{0}}}{1}".format(XMLIntf.namespace, rootNodeName)))
        
    def _createDocumentOptional(self, givendoc, rootNodeName):
        return self.createDocument(rootNodeName) if givendoc is None else givendoc
        
    def _getClassDoc(self, classType, doc):
        return self._createDocumentOptional(doc, self.Class2RootNode[classType])
        
    def _exportToDomSimple(self, obj, rootName, flags = None, doc = None):
        thisDoc = self._getClassDoc(type(obj), doc)
        obj.toDom(thisDoc.getroot(), flags)
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
        return self._exportToDomSimple(obj, self.Class2RootNode[type(obj)], flags, doc)
        
    def exportListToDom(self, list, classType, flags = None, doc = None):
        doc = self._getClassDoc(classType, doc)
        for obj in list:
            obj.toDom(doc.getroot(), flags)
        return doc
        
    def getImportContext(self):
        return Imports.ImportContext(self.store)
        
    def garbageCollection(self):
        staleBroadcasts = list((str(t[0]) for t in self.store.execute("""SELECT broadcasts.ID FROM broadcasts LEFT OUTER JOIN stations ON (broadcasts.StationID = stations.ID) WHERE stations.ID IS NULL""")))
        if len(staleBroadcasts) > 0:
            self.store.execute("""DELETE FROM broadcasts WHERE ID IN ({0})""".format(",".join(staleBroadcasts)))
        
        staleTransmissions = list((str(t[0]) for t in self.store.execute("""SELECT transmissions.ID FROM transmissions LEFT OUTER JOIN broadcasts ON (transmissions.BroadcastID = broadcasts.ID) WHERE broadcasts.ID IS NULL""")))
        if len(staleTransmissions) > 0:
            self.store.execute("""DELETE FROM transmissions WHERE ID IN ({0})""".format(",".join(staleTransmissions)))
            
        staleBroadcastFrequencies = list((str(t[0]) for t in self.store.execute("""SELECT broadcastFrequencies.ID FROM broadcastFrequencies LEFT OUTER JOIN broadcasts ON (broadcastFrequencies.BroadcastID = broadcasts.ID) WHERE broadcasts.ID IS NULL""")))
        if len(staleBroadcastFrequencies) > 0:
            self.store.execute("""DELETE FROM broadcastFrequencies WHERE ID IN ({0})""".format(",".join(staleBroadcastFrequencies)))
        
        foreignSupplementTables = {}
        staleForeignSupplements = list()
        for id, localID, fieldName in self.store.execute("""SELECT t.ID, t.LocalID, t.FieldName FROM foreignSupplement as t"""):
            partitioned = fieldName.partition(".")
            if len(partitioned[2]) == 0:
                staleForeignSupplements.append(str(id))
                continue
            tableName = partitioned[0]
            if not tableName in foreignSupplementTables:
                foreignSupplementTables[tableName] = list()
            foreignSupplementTables[tableName].append((localID, id))
        if len(staleForeignSupplements) > 0:
            self.store.execute("""DELETE FROM foreignSupplement WHERE ID IN ({0})""".format(",".join(staleForeignSupplements)))
        
        staleForeignSupplementCount = len(staleForeignSupplements)
        for table, items in foreignSupplementTables.iteritems():
            staleForeignSupplements = list((str(t[0]) for t in self.store.execute("""SELECT foreignSupplement.ID FROM foreignSupplement LEFT OUTER JOIN `{0}` ON (foreignSupplement.LocalID = `{0}`.ID) WHERE (`{0}`.ID IS NULL) AND (foreignSupplement.ID IN ({1}))""".format(table, ",".join((str(item[1]) for item in items))))))
            if len(staleForeignSupplements) > 0:
                self.store.execute("""DELETE FROM foreignSupplement WHERE ID IN ({0})""".format(",".join(staleForeignSupplements)))
            staleForeignSupplementCount += len(staleForeignSupplements)
            
        staleTXItemCount = 0
        for table in self.store.find(TransmissionClassTable):
            staleTXItems = list((str(t[0]) for t in self.store.execute("""SELECT `{0}`.ID FROM `{0}` LEFT OUTER JOIN transmissions ON (`{0}`.TransmissionID = transmissions.ID) WHERE transmissions.ID IS NULL""".format(table.TableName))))
            staleTXItemCount += len(staleTXItems)
            if len(staleTXItems) > 0:
                self.store.execute("""DELETE FROM `{0}` WHERE ID IN ({1})""".format(table.TableName, ",".join(staleTXItems)))
        
        return (len(staleBroadcasts), len(staleTransmissions), staleForeignSupplementCount, staleTXItemCount)
        
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
        if obj.Broadcast is not None:
            obj.Broadcast.transmissionRemoved()
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
        if self.Parent is not None:
            self.Parent.touch()
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
        if self.Station is not None:
            self.Station.broadcastRemoved()
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
        
    def normalizeDate(self, dateTime):
        return datetime(year=dateTime.year, month=dateTime.month, day=dateTime.day)
        
    def importTransaction(self, doc):
        context = self.getImportContext()
        for node in (node for node in doc.getroot()):
            tag = node.tag
            tagPart = tag.partition("}")
            if len(tagPart[1]) == 0:
                context.log("Encountered non-namespaced tag: {0}".format(tag))
                continue
            if tagPart[0][1:] != XMLIntf.namespace:
                context.log("Encountered tag with wrong namespace: {0}. Only namespace supported is {1}".format(tag, XMLIntf.importNamespace))
                continue
            tag = tagPart[2]
            if node.tag == u"delete":
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
                    }[tag]
                except KeyError:
                    context.log("Invalid transaction node: %s" % node.tagName)
                    continue
                context.importFromETree(node, cls)
        return context
        
    def getStation(self, stationDesignator, notModifiedCheck = None, head = False):
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
        if notModifiedCheck is not None:
            notModifiedCheck(station.Modified)
        return (station.Modified, station)
        
    def getCloseBroadcasts(self, stationId, time, jitter, notModifiedCheck = None, head = False):
        wideBroadcasts = self.store.find(Broadcast, Broadcast.StationID == stationId)
        lastModified = max(
            wideBroadcasts.max(Broadcast.Modified), 
            self.store.get(Station, stationId).BroadcastRemoved
        )
        if head:
            return (lastModified, None)
        if notModifiedCheck is not None:
            notModifiedCheck(lastModified)
        
        broadcasts = wideBroadcasts.find(And(
            And(
                Broadcast.BroadcastStart <= time + jitter,
                Broadcast.BroadcastEnd > time - jitter
            ),
            Broadcast.Type == u"data"
        ))
        return (lastModified, broadcasts)
        
    def listObjects(self, cls, limiter = None, notModifiedCheck = None, head = False):
        objects = self.store.find(cls)
        lastModified = objects.max(cls.Modified)
        if cls == Transmission:
            lastModified = max(lastModified, self.store.find(Broadcast).max(Broadcast.TransmissionRemoved))
        elif cls == Broadcast:
            lastModified = max(lastModified, self.store.find(Station).max(Station.BroadcastRemoved))
        if head:
            return (lastModified, None)
        if notModifiedCheck is not None:
            notModifiedCheck(lastModified)
        if limiter is not None:
            objects = limiter(objects)
        return (lastModified, objects)
    
    def getTransmissionsByMonth(self, stationId, year, month, limiter = None, notModifiedCheck = None, head = False):
        if month is not None:
            startTimestamp = datetime(year, month, 1)
            if month != 12:
                endTimestamp = datetime(year, month+1, 1)
            else:
                endTimestamp = datetime(year+1, 1, 1)
        else:
            startTimestamp = datetime(year, 1, 1)
            endTimestamp = datetime(year+1, 1, 1)
        startTimestamp = TimeUtils.toTimestamp(startTimestamp)
        endTimestamp = TimeUtils.toTimestamp(endTimestamp)
        
        transmissions = self.store.find((Transmission, Broadcast), 
            Transmission.BroadcastID == Broadcast.ID,
            And(Broadcast.StationID == stationId, 
                And(Transmission.Timestamp >= startTimestamp,
                    Transmission.Timestamp < endTimestamp)))
        lastModified = max(
            transmissions.max(Transmission.Modified), 
            self.store.find(Broadcast, Broadcast.StationID == stationId).max(Broadcast.TransmissionRemoved),
            self.store.get(Station, stationId).BroadcastRemoved
        )
        if head:
            return (lastModified, None)
        if notModifiedCheck is not None:
            notModifiedCheck(lastModified)
        transmissions.order_by(Asc(Transmission.Timestamp))
        if limiter is not None:
            transmissions = limiter(transmissions)
        return (lastModified, (transmission for (transmission, broadcast) in transmissions))
        
    def getTransmissionStats(self, stationId, notModifiedCheck = None, head = False):
        transmissions = self.store.find(Transmission, 
            Transmission.BroadcastID == Broadcast.ID, 
            Broadcast.StationID == stationId)
        lastModified = max(
            transmissions.max(Transmission.Modified),
            self.store.find(Broadcast, Broadcast.StationID == stationId).max(Broadcast.TransmissionRemoved),
            self.store.get(Station, stationId).BroadcastRemoved
        )
        if head:
            return (lastModified, None)
        if notModifiedCheck is not None:
            notModifiedCheck(lastModified)
        
        months = self.store.execute("SELECT YEAR(FROM_UNIXTIME(Timestamp)) as year, MONTH(FROM_UNIXTIME(Timestamp)) as month, COUNT(DATE_FORMAT(FROM_UNIXTIME(Timestamp), '%%Y-%%m')) FROM transmissions LEFT JOIN broadcasts ON (transmissions.BroadcastID = broadcasts.ID) WHERE broadcasts.StationID = '%d' GROUP BY year, month ORDER BY year ASC, month ASC" % (stationId))
        
        return (lastModified, months)
        
    def getUpcomingBroadcasts(self, station, all, update, timeLimit, maxTimeRange, limiter = None, notModifiedCheck = None, head = False):
        now = self.now()
        where = And(Or(Broadcast.BroadcastEnd > now, Broadcast.BroadcastEnd == None), (Broadcast.BroadcastStart < (now + timeLimit)))
        if not all:
            where = And(where, Broadcast.Type == u"data")
        if station is not None:
            where = And(where, Broadcast.StationID == stationId)
        
        broadcasts = self.store.find(Broadcast, where)
        lastModified = max(
            broadcasts.max(Broadcast.Modified),
            station.BroadcastRemoved if station is not None else None,
            station.Schedule.Modified if (station is not None and station.Schedule is not None) else None
        )
        if head:
            return (lastModified, None, None, None)
        if notModifiedCheck is not None:
            notModifiedCheck(lastModified)
        
        if update:
            untilDate = datetime.fromtimestamp(now)
            untilDate += timedelta(seconds=timeLimit)
            untilDate = self.normalizeDate(untilDate)
            
            until = self.toTimestamp(untilDate)
            
            if station is None:
                validUntil = self.scheduleMaintainer.updateSchedules(until, maxTimeRange)
            else:
                validUntil = self.scheduleMaintainer.updateSchedule(station, until, maxTimeRange)
            # trans.set_header_value("Expires", self.model.formatHTTPTimestamp(validUntil))
        return (lastModified, broadcasts if limiter is None else limiter(broadcasts), validUntil >= until, validUntil)
        
    def getStationFrequencies(self, station, notModifiedCheck = None, head = False):
        global UPCOMING, PAST, ONAIR
        broadcasts = self.store.find(Broadcast,
            Broadcast.StationID == station.ID)
        lastModified = max(
            broadcasts.max(Broadcast.Modified),
            station.BroadcastRemoved
        )
        if station.Schedule is not None:
            scheduleLeafs = self.store.find(ScheduleLeaf,
                ScheduleLeaf.StationID == station.ID)
            lastModified = lastModified if station.Schedule.Modified < lastModified else station.Schedule.Modified
        if head:
            return (lastModified, None)
        if notModifiedCheck is not None:
            notModifiedCheck(lastModified)
        
        if station.Schedule is None:
            now = self.now()
            frequencies = self.store.find(
                (Max(Broadcast.BroadcastEnd), Min(Broadcast.BroadcastStart), Broadcast.BroadcastStart > now, BroadcastFrequency.Frequency, Modulation.Name), 
                BroadcastFrequency.ModulationID == Modulation.ID,
                BroadcastFrequency.BroadcastID == Broadcast.ID,
                Broadcast.StationID == station.ID)
            frequencies.group_by(Or(Func("ISNULL", Broadcast.BroadcastEnd), And(Broadcast.BroadcastEnd >= now, Broadcast.BroadcastStart <= now)), Broadcast.BroadcastStart > now, BroadcastFrequency.Frequency, Modulation.Name)
            
            return (lastModified, ((freq, modulation, UPCOMING if isUpcoming == 1 else (ONAIR if lastUse is None else PAST), nextUse if isUpcoming else lastUse) for (lastUse, nextUse, isUpcoming, freq, modulation) in frequencies))
            
    def getDuplicateTransmissions(self, txTable, mainStation, matchFields = None, includeOtherStationsWithin = 86400, notModifiedCheck = None, head = False):
        txItem1 = ClassAlias(txTable.PythonClass, name="txItem1")
        txItem2 = ClassAlias(txTable.PythonClass, name="txItem2")
        
        tx1 = ClassAlias(Transmission, name="tx1")
        tx2 = ClassAlias(Transmission, name="tx2")
        
        bc1 = ClassAlias(Broadcast, name="broadcast1")
        bc2 = ClassAlias(Broadcast, name="broadcast2")
        
        on = txItem1.TransmissionID > txItem2.TransmissionID
        if matchFields is None:
            matchFields = txTable.PythonClass.fields
        for field in txTable.PythonClass.fields:
            cond = getattr(txItem1, field.FieldName) == getattr(txItem2, field.FieldName)
            on = And(on, cond)
        
        
        dupes = self.store.using(
            txItem1, 
            LeftJoin(tx1, on=(txItem1.TransmissionID == tx1.ID)), 
            LeftJoin(bc1, on=(tx1.BroadcastID == bc1.ID)),
            LeftJoin(txItem2, on=on), 
            LeftJoin(tx2, on=(txItem2.TransmissionID == tx2.ID)),
            LeftJoin(bc2, on=(tx2.BroadcastID == bc2.ID))
        ).find((bc1, tx1, txItem1, bc2, tx2, txItem2), 
            And(
                bc1.StationID == mainStation.ID,  
                Or(
                    bc2.StationID == mainStation.ID,
                    Func("ABS", (tx2.Timestamp - tx1.Timestamp) <= includeOtherStationsWithin)
                )
            )
        )
        
        lastModified = max(
            dupes.max(tx1.Modified),
            dupes.max(tx2.Modified),
            dupes.max(bc1.TransmissionRemoved),
            dupes.max(bc2.TransmissionRemoved),
            self.store.find(Station).max(Station.BroadcastRemoved)
        )
        if head:
            return (lastModified, None)
        if notModifiedCheck is not None:
            notModifiedCheck(lastModified)
            
            
        return (lastModified, dupes.order_by(Asc(tx1.Timestamp)))
            
