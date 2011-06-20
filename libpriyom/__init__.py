from storm.locals import *
from modulations import Modulation, Frequency
from broadcasts import BroadcastFrequency, Broadcast
from transmissions import Transmission, TransmissionClass, TransmissionClassTable, TransmissionClassTableField
from schedules import Schedule, ScheduleLeaf
from stations import Station
from foreign import ForeignSupplement
import xmlintf
from interface import PriyomInterface

BroadcastFrequency.Broadcast = Reference(BroadcastFrequency.BroadcastID, Broadcast.ID)
Broadcast.Station = Reference(Broadcast.StationID, Station.ID)
Broadcast.ScheduleLeaf = Reference(Broadcast.ScheduleLeafID, Broadcast.ID)
Broadcast.Transmissions = ReferenceSet(Broadcast.ID, Transmission.BroadcastID)
ScheduleLeaf.Station = Reference(ScheduleLeaf.StationID, Station.ID)
Schedule.Leaves = ReferenceSet(Schedule.ID, ScheduleLeaf.ScheduleID)
Station.Transmissions = ReferenceSet(Station.ID, Transmission.StationID)
Station.Broadcasts = ReferenceSet(Station.ID, Broadcast.StationID)
