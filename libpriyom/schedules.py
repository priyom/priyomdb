from storm.locals import *
import xmlintf
import modulations
import datetime
import formatting

class Schedule(object):
    __storm_table__ = "schedules"
    ID = Int(primary = True)
    ParentID = Int()
    Name = Unicode()
    ScheduleKind = Enum(map={
        "once": "once",
        "year": "year",
        "month": "month",
        "week": "week",
        "day": "day",
        "hour": "hour"
    })
    Skip = Int()
    Every = Int()
    StartTimeOffset = Int()
    EndTimeOffset = Int()
    
    def _formatOnce(self, start, end):
        return start.strftime(formatting.priyomdate), end.strftime(formatting.priyomdate)
    
    def _formatYear(self, start, end):
        return start.strftime("%b %d."), end.strftime("%b %d.")
    
    def _formatMonth(self, start, end):
        return start.strftime("%d"), end.strftime("%d")
    
    def _formatWeek(self, start, end):
        return start.strftime("%d. %H:%Mz"), end.strftime("%d. %H:%Mz")
    
    def _formatDay(self, start, end):
        return start.strftime("%H:%Mz"), end.strftime("%H:%Mz")
        
    def _formatHour(self, start, end):
        return start.strftime("minute %M"), end.strftime("minute %M")
    
    def toDom(self, parentNode, stationId = None):
        doc = parentNode.ownerDocument
        store = Store.of(self)
        schedule = doc.createElementNS(xmlintf.namespace, "schedule")
        
        xmlintf.appendTextElements(schedule,
            [
                ("id", unicode(self.ID)),
                ("name", self.Name)
            ]
        )
        if self.ScheduleKind == "once":
            xmlintf.appendTextElement(schedule, "no-repeat", "")
        else:
            repeat = xmlintf.appendTextElement(schedule, "repeat", unicode(self.Every), doNotAppend = True)
            repeat.setAttribute("step", self.ScheduleKind)
            repeat.setAttribute("skip", unicode(self.Skip))
            schedule.appendChild(repeat)
        
        start = datetime.datetime.utcfromtimestamp(self.StartTimeOffset)
        start = start - datetime.timedelta(hours=1)
        
        end = None
        if self.EndTimeOffset is not None:
            end = datetime.datetime.utcfromtimestamp(self.EndTimeOffset)
            end = end - datetime.timedelta(hours=1)
        else:
            end = datetime.datetime.utcfromtimestamp(0)
            
        startStr, endStr = {
            "once": self._formatOnce(start, end),
            "year": self._formatYear(start, end),
            "month": self._formatMonth(start, end),
            "week": self._formatWeek(start, end),
            "day": self._formatDay(start, end),
            "hour": self._formatHour(start, end)
        }[self.ScheduleKind]
        
        startOffset = xmlintf.appendTextElement(schedule, "start-offset", startStr)
        startOffset.setAttribute("seconds", unicode(self.StartTimeOffset))
        
        if self.EndTimeOffset is not None:
            endOffset = xmlintf.appendTextElement(schedule, "end-offset", endStr)
            endOffset.setAttribute("seconds", unicode(self.EndTimeOffset))
            
        schedules = doc.createElementNS(xmlintf.namespace, "schedules")
        for _schedule in self.Children:
            _schedule.toDom(schedules, stationId)
        schedule.appendChild(schedules)
        
        leaves = doc.createElementNS(xmlintf.namespace, "leaves")
        if stationId is not None:
            leavesSelect = store.find(ScheduleLeaf, 
                (ScheduleLeaf.StationID == stationId) and (ScheduleLeaf.ScheduleID == self.ID))
            for leaf in leavesSelect:
                leaf.toDom(leaves)
        else:
            for leaf in self.Leaves:
                leaf.toDom(leaves)
        schedule.appendChild(leaves)
                
        parentNode.appendChild(schedule)
        return schedule
    
Schedule.Parent = Reference(Schedule.ParentID, Schedule.ID)
Schedule.Children = ReferenceSet(Schedule.ID, Schedule.ParentID)
    
class ScheduleLeaf(object):
    __storm_table__ = "scheduleLeaves"
    ID = Int(primary = True)
    StationID = Int()
    ScheduleID = Int()
    Schedule = Reference(ScheduleID, Schedule.ID)
    FrequencyID = Int()
    Frequency = Reference(FrequencyID, modulations.Frequency.ID)
    BroadcastType = Enum(map={
        "data": "data",
        "continous": "continous"
    })
    
    def toDom(self, parentNode):
        doc = parentNode.ownerDocument
        leaf = doc.createElementNS(xmlintf.namespace, "leaf")
        xmlintf.appendTextElement(leaf, "kind", self.BroadcastType)
        self.Frequency.toDom(leaf)
        parentNode.appendChild(leaf)

