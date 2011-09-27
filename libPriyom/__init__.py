"""
File name: __init__.py
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
from Modulation import Modulation
from Broadcast import BroadcastFrequency, Broadcast
from Transmission import Transmission, TransmissionClass, TransmissionClassTable, TransmissionClassTableField
from Schedule import Schedule, ScheduleLeaf
from Station import Station
from Foreign import ForeignSupplement
import XMLIntf
from Interface import PriyomInterface
from TransmissionParser import TransmissionParserNode, TransmissionParserNodeField, NodeError
from Helpers import TimeUtils
from Event import Event, EventClass

BroadcastFrequency.Broadcast = Reference(BroadcastFrequency.BroadcastID, Broadcast.ID)
Broadcast.Station = Reference(Broadcast.StationID, Station.ID)
Broadcast.ScheduleLeaf = Reference(Broadcast.ScheduleLeafID, ScheduleLeaf.ID)
Broadcast.Transmissions = ReferenceSet(Broadcast.ID, Transmission.BroadcastID)
ScheduleLeaf.Station = Reference(ScheduleLeaf.StationID, Station.ID)
# Station.Transmissions = ReferenceSet(Station.ID, Transmission.StationID)
Station.Broadcasts = ReferenceSet(Station.ID, Broadcast.StationID)
