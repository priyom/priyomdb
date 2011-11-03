"""
File name: UITree.py
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
from libPriyom import *
#from Components import Input, TextArea, Select, SelectStormObject, VirtualTable, Table, TableGroup, IDTableGroup, Timestamp, CheckBox, ForeignInput, TransmissionContents, BroadcastFrequencies, StormColumn, ReferenceColumn, IDColumn, TimestampColumn, CreatedColumn, ModifiedColumn, ReferencingTable
from PriyomHTTP.Server.Resources.Admin.Components import *


"""u"schedules": VirtualTable(u"Schedule database", Schedule, 
    EditorTable(
        IDEditorGroup(u"Basic information",
            Input(
                name=u"Name",
                caption=u"Display name"
                description=u"Name shown in tables etc. and on the page"
            ),
            Timestamp(
                name=u"StartTimeOffset",
                caption=u"Valid from",
                description=u"Date after which the schedule should be in effect"
            ),
            Timestamp(
                name=u"EndTimeOffset",
                caption=u"Valid until",
                description=u"Date until which the schedule should be in effect"
            )
        )
    ),
    EditorSplitPanel(
        ScheduleTreeView(u"Schedule tree"),
        ScheduleChildEditor(
            
        )
    ),
    where=(Schedule.Parent == None),
    relatedTables=(
        ReferencingVirtualTable(u"station", match=Station.Schedule)
    ),
    multiEdit=False
),"""

virtualTables = {
    u"stations": VirtualTable(u"stations", Station, 
        Table(
            IDTableGroup(u"Identification",
                Input(
                    name=u"EnigmaIdentifier", 
                    caption=u"Enigma identifier", 
                    description=u"One of the well known enigma identifiers"
                ),
                Input(
                    name=u"PriyomIdentifier",
                    caption=u"Priyom identifier",
                    description=u"If available, the priyom identifer"
                ),
                Input(
                    name=u"Nickname",
                    description=u"Nickname of the station (e.g. Buzzer for S28)"
                )
            ),
            TableGroup(u"Description",
                TextArea(
                    name=u"Description", 
                    description=u"A longer description of the station which may contain valid XHTML.",
                    fullWidth=True
                ),
                Input(
                    name=u"Status",
                    description=u"Current status (e.g. Active or Inactive)",
                ),
                Input(  
                    name=u"Location",
                    description=u"Location (or at least a guess)"
                )
            ),
            TableGroup(u"Schedule",
                CheckBox(
                    name=u"ScheduleConfirmed",
                    caption=u"Schedule confirmed"
                ),
                SelectStormObject(
                    name=u"Schedule",
                    caption=u"Schedule object",
                    description=u"Select the schedule object from the database",
                    withMakeSingleUser=True,
                    withEdit=True,
                    withNone=u"No schedule assigned",
                    #virtualTable=u"schedules"
                    stormClass=Schedule,
                    where=(Schedule.Parent == None)
                )
            )
        ),
        description=u"Shortwave station registry",
        columns=(
            IDColumn(Station),
            CreatedColumn(Station),
            ModifiedColumn(Station),
            StormColumn(u"Enigma ID", Station.EnigmaIdentifier, width="8em"),
            StormColumn(u"Priyom ID", Station.PriyomIdentifier, width="8em"),
            StormColumn(u"Nickname", Station.Nickname)
        ),
        referencingTables=(
            ReferencingTable(u"broadcasts", Broadcast, Broadcast.StationID, u"Broadcasts of this station"),
        )
    ),
    u"broadcasts": VirtualTable(u"broadcasts", Broadcast, 
        Table(
            IDTableGroup(u"Basic information",
                SelectStormObject(
                    name=u"Station",
                    description=u"Station the broadcast is assigned to",
                    stormClass=Station
                ),
                Select(
                    name=u"Type",
                    description=u"The broadcast type. This must be data if transmissions are assigned",
                    items=[
                        (u"continous", u"Continous (e.g. Channel marker)", lambda bc: Store.of(bc) is None or bc.Transmissions.count() == 0),
                        (u"data", u"Data broadcast (i.e. containing transmissions)", True)
                    ]
                ),
                CheckBox(
                    name=u"Confirmed",
                    caption=u"Confirmed",
                    description=u"Whether the broadcast is confirmed to have taken place"
                ),
                TextArea(
                    name=u"Comment",
                    caption=u"Comment",
                    description=u"Any comment?"
                )
            ),
            TableGroup(u"Timing and schedule",
                Timestamp(
                    name=u"BroadcastStart",
                    caption=u"Starts at",
                    description=u"Time at which the broadcast started (UTC)",
                ),
                Timestamp(
                    name=u"BroadcastEnd",
                    caption=u"Ends at",
                    description=u"Time at which the broadcast ended (UTC)",
                    allowNone=True
                ),
                Input(
                    name=u"ScheduleLeafID",
                    caption=u"Schedule association ID",
                    description=u"Identifies this broadcast as created by a schedule",
                    disabled=True
                )
            ),
            TableGroup(u"Frequencies",
                BroadcastFrequencies(
                    name=u"Frequencies",
                    description=u"The frequencies this broadcast is on."
                )
            )
        ),
        description=u"Broadcast database",
        columns=(
            IDColumn(Broadcast),
            CreatedColumn(Broadcast),
            ModifiedColumn(Broadcast),
            TimestampColumn(u"Start time", Broadcast.BroadcastStart),
            TimestampColumn(u"End time", Broadcast.BroadcastEnd),
            StormColumn(u"Type", Broadcast.Type),
            ReferenceColumn(u"Station", Broadcast.Station, Station, u"Station", sortingColumns=(
                Station.EnigmaIdentifier,
                Station.PriyomIdentifier,
                Station.Nickname
            )),
        ),
        referencingTables=(
            ReferencingTable(u"transmissions", Transmission, Transmission.BroadcastID, u"Transmissions of this broadcast"),
        )
        #relatedTables=(
        #    ReferenedVirtualTable(u"stations", match=Broadcast.Station),
        #    ReferencingVirtualTable(u"transmission", match=Transmission.Broadcast)
        #)
    ),
    u"transmissions": VirtualTable(u"transmissions", Transmission,
        Table(
            IDTableGroup(u"Basic information",
                Timestamp(
                    name=u"Timestamp",
                    description=u"Timestamp at which the transmission started"
                ),
                ForeignInput(
                    name=u"Callsign",
                    foreignName=u"ForeignCallsign",
                    description=u"The callsign used in the transmission (see priyom.org callsign policies for a reference)"
                ),
                SelectStormObject(
                    name=u"Class",
                    description=u"Transmission format class; This defines the format of the contents of the transmission",
                    disabled=lambda tx: len(tx.blocks) > 0,
                    stormClass=TransmissionClass
                )
            ),
            TableGroup(u"Media",
                Input(
                    name=u"RecordingURL",
                    description=u"URL referencing a recording if the transmission. Should be on priyom.org domain"
                ),
                TextArea(
                    name=u"Remarks",
                    description=u"Any remarks about the transmission (like voice sex etc.)"
                )
            ),
            TableGroup(u"Contents",
                TransmissionContents(
                    name=u"Contents",
                    description=u"Contents of the transmission. The format of this depends on the selected transmission class."
                )
            )
        ),
        description=u"Transmission database",
        columns=(
            IDColumn(Transmission),
            CreatedColumn(Transmission),
            ModifiedColumn(Transmission),
            TimestampColumn(u"Timestamp", Transmission.Timestamp),
            StormColumn(u"Callsign", Transmission.Callsign)
        )
    )
}
