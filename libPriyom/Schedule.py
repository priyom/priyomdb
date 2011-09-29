"""
File name: Schedule.py
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
import xml.dom.minidom as dom
import XMLIntf
from Modulation import Modulation
import datetime
import Formatting
from PriyomBase import PriyomBase

class Schedule(PriyomBase, XMLIntf.XMLStorm):
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
    
    @staticmethod
    def checkNestable(parentKind, childKind):
        if parentKind == "once":
            return childKind in ["year", "month", "week", "day", "hour"]
        elif parentKand == "year":
            return childKind in ["month", "week", "day", "hour"]
        elif parentKind == "month":
            return childKind in ["week", "day", "hour"]
        elif parentKind == "week":
            return childKind in ["day", "hour"]
        elif parentKind == "day":
            return childKind in ["hour"]
        elif parentKind == "hour":
            return False
        else:
            return False
    
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
        
    def _leavesFromDom(self, node, context):
        for node in (node for node in node.childNodes if node.nodeType == dom.Node.ELEMENT_NODE):
            if node.tagName != "leaf":
                context.log("Found invalid node in schedule.leaves. Skipping.")
                continue
            leaf = ScheduleLeaf()
            self.store.add(leaf)
            leaf.Schedule = self
            leaf.fromDom(leaf)
            
    def _schedulesFromDom(self, node, context):
        for node in (node for node in node.childNodes if node.nodeType == dom.Node.ELEMENT_NODE):
            if node.tagName != "schedule-reference":
                context.log("Found invalid node in schedule.schedules. Skipping.")
                continue
            try:
                id = int(node.getAttribute("id"))
            except:
                context.log("Schedule references in schedule.schedules must consist only of <schedule id=\"id\" />")
                continue
            schedule = self.store.get(Schedule, id)
            if schedule is not None:
                if schedule.Parent is not None:
                    context.log("Schedule %d is already assigned to another parent." % (schedule.ID))
                    continue
                if not Schedule.checkNestable(self.ScheduleKind, schedule.ScheduleKind):
                    context.log("Cannot nest a \"%s\" schedule into a \"%s\" schedule." % (self.ScheduleKind, schedule.ScheduleKind))
                    continue
                schedule.Parent = self
        
    def loadDomElement(self, node, context):
        if node.tagName == "repeat":
            self.ScheduleKind = node.getAttribute("step")
            self.Skip = node.getAttribute("skip")
            self.Every = XMLIntf.getText(node)
        elif node.tagName == "name":
            self.Name = XMLIntf.getText(node)
        elif node.tagName == "start-offset":
            self.StartTimeOffset = node.getAttribute("seconds")
        elif node.tagName == "end-offset":
            self.EndTimeOffset = node.getAttribute("seconds")
        elif node.tagName == "leaves":
            for leaf in list(self.Leaves):
                leaf.delete()
            self._leavesFromDom(node, context)
        elif node.tagName == "schedules":
            for schedule in list(self.Children):
                schedule.Parent = None
            self._schedulesFromDom(node, context)
            
    def touch(self, newModified = None):
        super(Schedule, self).touch(newModified)
        if self.Parent is None:
            return
        if self.Modified > self.Parent.Modified:
            self.Parent.touch(self.Modified)
        
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
    Modulation = Reference(ModulationID, Modulation.ID)
    
    def fromDom(self, node, context):
        self.Frequency = int(XMLIntf.getText(node))
        self.Modulation = Store.of(self).find(Modulation, Modulation.Name == node.getAttribute("modulation")).any()
        if self.Modulation is None:
            self.Modulation = Modulation()
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
        
    def delete(self):
        Frequencies.remove()
        Store.of(self).remove(self)
    
    def toDom(self, parentNode):
        doc = parentNode.ownerDocument
        leaf = doc.createElementNS(XMLIntf.namespace, "leaf")
        XMLIntf.appendTextElements(leaf, {
            "kind": self.BroadcastType,
            "station-id": self.StationID
        })
        # self.Frequency.toDom(leaf)
        for frequency in self.Frequencies:
            frequency.toDom(leaf)
        parentNode.appendChild(leaf)

Schedule.Leaves = ReferenceSet(Schedule.ID, ScheduleLeaf.ScheduleID)
