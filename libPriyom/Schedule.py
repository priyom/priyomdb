from storm.locals import *
import XMLIntf
import Modulation
import datetime
import Formatting

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
        return start.strftime(Formatting.priyomdate), end.strftime(Formatting.priyomdate)
    
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
        schedule = doc.createElementNS(XMLIntf.namespace, "schedule")
        
        XMLIntf.appendTextElements(schedule,
            [
                ("id", unicode(self.ID)),
                ("name", self.Name)
            ]
        )
        if self.ScheduleKind == "once":
            XMLIntf.appendTextElement(schedule, "no-repeat", "")
        else:
            repeat = XMLIntf.appendTextElement(schedule, "repeat", unicode(self.Every), doNotAppend = True)
            repeat.setAttribute("step", self.ScheduleKind)
            repeat.setAttribute("skip", unicode(self.Skip))
            schedule.appendChild(repeat)
        
        start = datetime.datetime.fromtimestamp(self.StartTimeOffset)
        start = start - datetime.timedelta(hours=1)
        
        end = None
        if self.EndTimeOffset is not None:
            end = datetime.datetime.fromtimestamp(self.EndTimeOffset)
            end = end - datetime.timedelta(hours=1)
        else:
            end = datetime.datetime.fromtimestamp(0)
            
        startStr, endStr = {
            "once": self._formatOnce(start, end),
            "year": self._formatYear(start, end),
            "month": self._formatMonth(start, end),
            "week": self._formatWeek(start, end),
            "day": self._formatDay(start, end),
            "hour": self._formatHour(start, end)
        }[self.ScheduleKind]
        
        startOffset = XMLIntf.appendTextElement(schedule, "start-offset", startStr)
        startOffset.setAttribute("seconds", unicode(self.StartTimeOffset))
        
        if self.EndTimeOffset is not None:
            endOffset = XMLIntf.appendTextElement(schedule, "end-offset", endStr)
            endOffset.setAttribute("seconds", unicode(self.EndTimeOffset))
            
        schedules = doc.createElementNS(XMLIntf.namespace, "schedules")
        for _schedule in self.Children:
            _schedule.toDom(schedules, stationId)
        schedule.appendChild(schedules)
        
        leaves = doc.createElementNS(XMLIntf.namespace, "leaves")
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
        
    def __repr__(self):
        return '<Schedule id="%d" kind="%s" start-offset="%d" end-offset="%r">%s</Schedule>' % (self.ID, self.ScheduleKind, self.StartTimeOffset, self.EndTimeOffset, self.Name)
        
    def __str__(self):
        return 'Schedule "%s"' % (self.Name)
    
Schedule.Parent = Reference(Schedule.ParentID, Schedule.ID)
Schedule.Children = ReferenceSet(Schedule.ID, Schedule.ParentID)

class ScheduleLeafFrequency(object):
    __storm_table__ = "scheduleLeafFrequencies"
    ID = Int(primary = True)
    ScheduleLeafID = Int()
    Frequency = Int()
    ModulationID = Int()
    Modulation = Reference(ModulationID, modulations.Modulation.ID)
    
    def fromDom(self, node):
        self.Frequency = int(XMLIntf.getText(node))
        self.Modulation = Store.of(self).find(modulations.Modulation, modulations.Modulation.Name == node.getAttribute("modulation")).any()
        if self.Modulation is None:
            self.Modulation = modulations.Modulation()
            Store.of(self).add(self.Modulation)
            self.Modulation.Name = node.getAttribute("modulation")
    
    def toDom(self, parentNode):
        doc = parentNode.ownerDocument
        frequency = XMLIntf.buildTextElementNS(doc, "frequency", unicode(self.Frequency), XMLIntf.namespace)
        frequency.setAttribute("modulation", self.Modulation.Name)
        parentNode.appendChild(frequency)

    
class ScheduleLeaf(object):
    __storm_table__ = "scheduleLeaves"
    ID = Int(primary = True)
    StationID = Int()
    ScheduleID = Int()
    Schedule = Reference(ScheduleID, Schedule.ID)
    Frequencies = ReferenceSet(ID, ScheduleLeafFrequency.ScheduleLeafID)
    BroadcastType = Enum(map={
        "data": "data",
        "continous": "continous"
    })
    
    def toDom(self, parentNode):
        doc = parentNode.ownerDocument
        leaf = doc.createElementNS(XMLIntf.namespace, "leaf")
        XMLIntf.appendTextElement(leaf, "kind", self.BroadcastType)
        # self.Frequency.toDom(leaf)
        for frequency in self.Frequencies:
            frequency.toDom(leaf)
        parentNode.appendChild(leaf)

