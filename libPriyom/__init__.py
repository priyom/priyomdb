from storm.locals import *
from Modulation import Modulation
from Broadcast import BroadcastFrequency, Broadcast
from Transmission import Transmission, TransmissionClass, TransmissionClassTable, TransmissionClassTableField
from Schedule import Schedule, ScheduleLeaf
from Station import Station
from Foreign import ForeignSupplement
import XMLIntf
from Interface import PriyomInterface

BroadcastFrequency.Broadcast = Reference(BroadcastFrequency.BroadcastID, Broadcast.ID)
Broadcast.Station = Reference(Broadcast.StationID, Station.ID)
Broadcast.ScheduleLeaf = Reference(Broadcast.ScheduleLeafID, ScheduleLeaf.ID)
Broadcast.Transmissions = ReferenceSet(Broadcast.ID, Transmission.BroadcastID)
ScheduleLeaf.Station = Reference(ScheduleLeaf.StationID, Station.ID)
Schedule.Leaves = ReferenceSet(Schedule.ID, ScheduleLeaf.ScheduleID)
Station.Transmissions = ReferenceSet(Station.ID, Transmission.StationID)
Station.Broadcasts = ReferenceSet(Station.ID, Broadcast.StationID)
