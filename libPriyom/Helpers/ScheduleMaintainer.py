from storm.locals import *
from ..broadcasts import Broadcast, BroadcastFrequency
from ..schedules import Schedule, ScheduleLeaf
from ..stations import Station
from time import mktime
from datetime import datetime, timedelta
from ..limits import limits

class ScheduleMaintainerError(Exception):
    pass
        
class LeafDescriptor(object):
    def __init__(self, leaf, startOffset):
        self.leaf = leaf
        self.startOffset = startOffset
    
class LeafList(object):
    def __init__(self, store, station):
        self.items = []
        self.store = store
        self.station = station
        self.stationId = station.ID
    
    def add(self, scheduleNode, instanceStartOffset):
        i = 0
        for leaf in self.store.find(ScheduleLeaf, 
            ScheduleLeaf.StationID == self.stationId,
            ScheduleLeaf.ScheduleID == scheduleNode.ID):
            
            self.items.append(LeafDescriptor(leaf, instanceStartOffset))
            i += 1
        return i
        
class UpdateContext(object):
    def __init__(self, rootSchedule, station, store, intervalStart, intervalEnd):
        self.rootSchedule = rootSchedule
        self.station = station
        self.store = store
        self.leafList = LeafList(store, station)
        self.intervalStart = intervalStart
        self.intervalEnd = intervalEnd

class ScheduleMaintainer(object):
    def __init__(self, store):
        self.store = store
        
    @staticmethod
    def now():
        return int(mktime(datetime.utcnow().timetuple()))
        
    @staticmethod
    def toTimestamp(datetime):
        return int(mktime(datetime.timetuple()))
        
    @staticmethod
    def incYear(dt, by):
        year = dt.year + by
        return datetime(year=year, month=1, day=1)
        
    @staticmethod
    def incMonth(dt, by):
        month = dt.month + by
        year = dt.year + int((month-1) / 12)
        month -= int((month-1) / 12) * 12
        return datetime(year=year, month=month, day=1)
        
    def getLeavesInIntervalRecurse(self, context, node, lowerConstraint, upperConstraint, allowLeaf = True):
        hasChildren = False
        for child in node.Children:
            hasChildren = True
            self.getLeavesInInterval(context, child, lowerConstraint, upperConstraint)
        if not hasChildren and allowLeaf:
            context.leafList.add(node, lowerConstraint - node.StartTimeOffset)
        
    def getLeavesInInterval_once(self, context, node, lowerConstraint, upperConstraint):
        if node.Parent is None:
            lc = max(lowerConstraint, node.StartTimeOffset)
            if node.EndTimeOffset is None:
                uc = upperConstraint
            else:
                uc = min(upperConstraint, node.EndTimeOffset)
        else:
            lc = lowerConstraint + node.StartTimeOffset
            uc = min(lowerConstraint + node.EndTimeOffset, upperConstraint)
        if (lc >= context.intervalStart):
            self.getLeavesInIntervalRecurse(context, node, lc, uc, node.Parent is not None)
            
    def getLeavesInInterval_year(self, context, node, lowerConstraint, upperConstraint):
        lcDate = datetime.fromtimestamp(lowerConstraint)
        lcDate = datetime(year=lcDate.year + node.Skip, month=1, day=1)
        ucDate = datetime(year=lcDate.year + 1, month=1, day=1)
        lc = ScheduleMaintainer.toTimestamp(lcDate)
        uc = ScheduleMaintainer.toTimestamp(ucDate)
        
        upperLimit = min(upperConstraint, context.intervalEnd)
        while (lc < upperLimit):
            if (uc > lowerConstraint):
                self.getLeavesInIntervalRecurse(context, node, lc + node.StartTimeOffset, min(lc + node.EndTimeOffset, upperConstraint, uc), lc >= context.intervalStart)
            if node.Every is None:
                break
            lcDate = ScheduleMaintainer.incYear(lcDate, node.Every)
            ucDate = ScheduleMaintainer.incYear(lcDate, 1)
            lc = ScheduleMaintainer.toTimestamp(lcDate)
            uc = ScheduleMaintainer.toTimestamp(ucDate)
            
    def getLeavesInInterval_month(self, context, node, lowerConstraint, upperConstraint):
        lcDate = datetime.fromtimestamp(lowerConstraint)
        lcDate = ScheduleMaintainer.incMonth(datetime(year=lcDate.year, month=1, day=1), node.Skip)
        ucDate = ScheduleMaintainer.incMonth(lcDate, 1)
        lc = ScheduleMaintainer.toTimestamp(lcDate)
        uc = ScheduleMaintainer.toTimestamp(ucDate)
        
        upperLimit = min(upperConstraint, context.intervalEnd)
        while (lc < upperLimit):
            if (uc > lowerConstraint):
                self.getLeavesInIntervalRecurse(context, node, lc + node.StartTimeOffset, min(lc + node.EndTimeOffset, upperConstraint, uc), lc >= context.intervalStart)
            if node.Every is None:
                break
            lcDate = ScheduleMaintainer.incMonth(lcDate, node.Every)
            ucDate = ScheduleMaintainer.incMonth(lcDate, 1)
            lc = ScheduleMaintainer.toTimestamp(lcDate)
            uc = ScheduleMaintainer.toTimestamp(ucDate)
            
    def _handleDeltaRepeat(self, context, node, lowerConstraint, upperConstraint, lcDate, interval):
        ucDate = lcDate + interval
        lc = ScheduleMaintainer.toTimestamp(lcDate)
        uc = ScheduleMaintainer.toTimestamp(ucDate)
        
        upperLimit = min(upperConstraint, context.intervalEnd)
        while (lc < upperLimit):
            if (uc > lowerConstraint):
                self.getLeavesInIntervalRecurse(context, node, lc + node.StartTimeOffset, min(lc + node.EndTimeOffset, upperConstraint, uc), lc >= context.intervalStart)
            if node.Every is None:
                break
            lcDate += interval * node.Every
            ucDate = lcDate + interval
            lc = ScheduleMaintainer.toTimestamp(lcDate)
            uc = ScheduleMaintainer.toTimestamp(ucDate)
        
    def getLeavesInInterval_week(self, context, node, lowerConstraint, upperConstraint):
        lcDate = datetime.fromtimestamp(lowerConstraint)
        lcDate = datetime(year=lcDate.year, month=lcDate.month, day=lcDate.day)
        interval = timedelta(days=7)
        
        self._handleDeltaRepeat(context, node, lowerConstraint, upperConstraint, lcDate, interval)
        
    def getLeavesInInterval_day(self, context, node, lowerConstraint, upperConstraint):
        lcDate = datetime.fromtimestamp(lowerConstraint)
        lcDate = datetime(year=lcDate.year, month=lcDate.month, day=lcDate.day)
        interval = timedelta(days=1)
        
        self._handleDeltaRepeat(context, node, lowerConstraint, upperConstraint, lcDate, interval)
        
    def getLeavesInInterval_hour(self, context, node, lowerConstraint, upperConstraint):
        lcDate = datetime.fromtimestamp(lowerConstraint)
        lcDate = datetime(year=lcDate.year, month=lcDate.month, day=lcDate.day)
        interval = timedelta(hours=1)
        
        self._handleDeltaRepeat(context, node, lowerConstraint, upperConstraint, lcDate, interval)
        
    def getLeavesInInterval(self, context, node, lowerConstraint, upperConstraint):
        method = getattr(self, "getLeavesInInterval_"+node.ScheduleKind)
        method(context, node, lowerConstraint, upperConstraint)
        
    def getLeavesInIntervalFromRoot(self, station, intervalStart, intervalEnd):
        if station.Schedule is None:
            raise ScheduleMaintainerError("Station %s has no schedule assigned" % (str(station)))
        context = UpdateContext(station.Schedule, station, self.store, intervalStart, intervalEnd)
        self.getLeavesInInterval(context, context.rootSchedule, intervalStart, intervalEnd)
        return context.leafList.items
        
    def _rebuildStationSchedule(self, station, start, end):
        self.store.find(Broadcast, Broadcast.StationID == station.ID, Broadcast.ScheduleLeaf != None, Broadcast.BroadcastStart > start).remove()
        leaves = self.getLeavesInIntervalFromRoot(station, start, end)
        for leaf in leaves:
            newBroadcast = Broadcast()
            self.store.add(newBroadcast)
            schedule = leaf.leaf.Schedule
            newBroadcast.BroadcastStart = schedule.StartTimeOffset + leaf.startOffset
            newBroadcast.BroadcastEnd = schedule.EndTimeOffset + leaf.startOffset
            newBroadcast.Type = leaf.leaf.BroadcastType
            for frequency in leaf.leaf.Frequencies:
                newFreq = BroadcastFrequency()
                self.store.add(newFreq)
                newFreq.Frequency = frequency.Frequency
                newFreq.ModulationID = frequency.ModulationID
                newBroadcast.Frequencies.add(newFreq)
            newBroadcast.Confirmed = False
            newBroadcast.Comment = None
            newBroadcast.Station = station
            newBroadcast.ScheduleLeaf = leaf.leaf
        station.ScheduleUpToDateUntil = end
        
    def updateSchedule(self, station, until, limit = None):
        now = ScheduleMaintainer.now()
        if station.Schedule is None:
            return until
        if (until - now) > limits.schedule.maxLookahead:
            until = now + limits.schedule.maxLookahead
        if station.ScheduleUpToDateUntil is None:
            start = now
        else:
            start = station.ScheduleUpToDateUntil
        if until <= start:
            return start
        if limit is not None and (until - start) > limit:
            until = start + limit
        self._rebuildStationSchedule(station, start, until)
        return until
    
    def updateSchedules(self, until, limit = None):
        now = ScheduleMaintainer.now()
        if until < now:
            return now
        if (until - now) > limits.schedule.maxLookahead:
            until = now + limits.schedule.maxLookahead
        validUntil = until
        if limit is None:
            limit = until
        for station in self.store.find(Station, Station.Schedule != None, Or(Station.ScheduleUpToDateUntil < until, Station.ScheduleUpToDateUntil == None)):
            start = now
            if station.ScheduleUpToDateUntil is not None:
                start = station.ScheduleUpToDateUntil
                if until <= start:
                    continue
            if (until - start) > limit:
                self._rebuildStationSchedule(station, start, start+limit)
                validUntil = min(validUntil, start+limit)
            else:
                self._rebuildStationSchedule(station, start, until)
        return validUntil
        
