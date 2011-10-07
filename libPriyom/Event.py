"""
File name: Event.py
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
from Station import Station
from PriyomBase import PriyomBase
import Formatting
import XMLIntf
import Helpers.TimeUtils as TimeUtils

class EventClass(object):
    __storm_table__ = "eventClasses"
    
    ID = Int(primary=True)
    Title = Unicode()
    StateChanging = Bool()
    
    def toTree(self, parent):
        eventClass = XMLIntf.SubElement(parent, u"event-class")
        XMLIntf.appendTextElements(eventClass, 
            (
                (u"ID", self.ID),
                (u"Title", self.Title)
            )
        )
        return eventClass
        
    def __unicode__(self):
        return self.Title
    
class Event(PriyomBase):
    __storm_table__ = "events"
    
    ID = Int(primary=True)
    Created = Int()
    Modified = Int()
    StationID = Int()
    Station = Reference(StationID, Station.ID)
    EventClassID = Int()
    EventClass = Reference(EventClassID, EventClass.ID)
    Description = Unicode()
    StartTime = Int()
    EndTime = Int()
    
    def toTree(self, parent):
        event = XMLIntf.SubElement(parent, u"event")
        XMLIntf.appendTextElements(event,
            (
                (u"ID", self.ID),
                (u"StationID", self.StationID),
                (u"Description", self.Description)
            )
        )
        if self.EventClass is not None:
            self.EventClass.toTree(event)
        else:
            XMLIntf.SubElement(parent, u"raw-event")
        XMLIntf.appendDateElement(event, u"StartTime", self.StartTime)
        if self.EndTime is not None:
            XMLIntf.appendDateElement(event, u"EndTime", self.EndTime)
        return event
        
    def __unicode__(self):
        return u"{1} event {0} at {2}".format(
            self.Description,
            unicode(self.EventClass) if self.EventClass is not None else u"raw",
            TimeUtils.fromTimestamp(self.StartTime).strftime(Formatting.priyomdate)
        )
