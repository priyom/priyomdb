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

class EventClass(object):
    __storm_table__ = "eventClass"
    
    ID = Int(primary=True)
    Title = Unicode()
    
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
