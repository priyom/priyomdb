from libPriyom import *
from EditComponents import Input, TextArea, Select, SelectStormObject, VirtualTable, Table, TableGroup, IDTableGroup, Timestamp, CheckBox

virtualTables = {
    u"stations": VirtualTable(u"Shortwave station registry", Station, 
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
                    name=u"Confirmed",
                    caption=u"schedule confirmed"
                ),
                SelectStormObject(
                    name=u"Schedule",
                    caption=u"Schedule object",
                    description=u"Select the schedule object from the database",
                    withMakeSingleUser=True,
                    withEdit=True,
                    #virtualTable=u"schedules"
                    cls=Schedule,
                    where=(Schedule.Parent == None)
                )
            )
        ),
        #relatedTables=(
        #    ReferencingVirtualTable(u"broadcasts", match=Broadcast.Station),
        #    ReferencedVirtualTable(u"schedules", match=Station.Schedule)
        #)
    ),
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
    u"broadcasts": VirtualTable(u"Broadcast database", Broadcast, 
        Table(
            IDTableGroup(u"Basic information",
                Select(
                    name=u"Type",
                    description=u"The broadcast type. This must be data if transmissions are assigned",
                    items=[
                        (u"continous", u"Continous (e.g. Channel marker)", lambda bc: bc.Transmissions.count() == 0),
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
                    description=u"Time at which the broadcast ended (UTC)"
                ),
                Input(
                    name=u"ScheduleLeafID",
                    caption=u"Schedule association ID",
                    description=u"Identifies this broadcast as created by a schedule",
                    disabled=True
                )
            )
        ),
        #relatedTables=(
        #    ReferenedVirtualTable(u"stations", match=Broadcast.Station),
        #    ReferencingVirtualTable(u"transmission", match=Transmission.Broadcast)
        #)
    ),
    u"transmissions": VirtualTable(u"Transmission database", Transmission,
        Table(
            IDTableGroup(u"Basic information",
                Timestamp(
                    name=u"Timestamp",
                    description=u"Timestamp at which the transmission started"
                ),
                ForeignInput(
                    name=u"Callsign",
                    foreignAttribute=u"ForeignCallsign",
                    description=u"The callsign used in the transmission (see priyom.org callsign policies for a reference)"
                ),
                SelectStormObject(
                    name=u"Class",
                    description=u"Transmission format class; This defines the format of the contents of the transmission",
                    disabled=lambda tx: len(tx.blocks) > 0
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
            )
        )
    )
}
