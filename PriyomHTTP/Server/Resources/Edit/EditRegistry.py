from EditResource import EditorGroup, EditorTable, InputEditor, SelectStormObjectEditor
from libPriyom import *

"""InputEditor(
                    name=u"ID", 
                    caption=u"Internal ID",
                    description=u"Used for database purposes. You can also use this to query the station by /station/ID"
                    disabled=True
                ),
                DateEditor(
                    name=u"Created",
                    caption=u"Created at",
                    disabled=True
                ),
                DateEditor(
                    name=u"Modified",
                    caption=u"Last modified",
                    disabled=True
                ),"""

virtualTables = {
    u"stations": VirtualTable(u"Shortwave station registry", Station, 
        EditorTable(
            IDEditorGroup(u"Identification",
                InputEditor(
                    name=u"EnigmaIdentifier", 
                    caption=u"Enigma identifier", 
                    description=u"One of the well known enigma identifiers"
                ),
                InputEditor(
                    name=u"PriyomIdentifier",
                    caption=u"Priyom identifier",
                    description=u"If available, the priyom identifer"
                ),
                InputEditor(
                    name=u"Nickname",
                    description=u"Nickname of the station (e.g. Buzzer for S28)"
                )
            ),
            EditorGroup(u"Description",
                TextAreaEditor(
                    name=u"Description", 
                    description=u"A longer description of the station which may contain valid XHTML.",
                    fullWidth=True
                ),
                InputEditorWithSelect(u"Status", [u"Active", u"Inactive"]),
                InputEditor(u"Location")
            ),
            EditorGroup(u"Schedule",
                CheckBoxEditor(
                    name=u"Confirmed",
                    caption=u"schedule confirmed"
                ),
                SelectStormObjectEditor(
                    name=u"Schedule",
                    caption=u"Schedule object",
                    description=u"Select the schedule object from the database",
                    withMakeSingleUser=True,
                    withEdit=True,
                    virtualTable=u"schedules"
                )
            )
        ),
        relatedTables=(
            ReferencingVirtualTable(u"broadcasts", match=Broadcast.Station),
            ReferencedVirtualTable(u"schedules", match=Station.Schedule)
        )
    ),
    u"schedules": VirtualTable(u"Schedule database", Schedule, 
        EditorTable(
            IDEditorGroup(u"Basic information",
                InputEditor(
                    name=u"Name",
                    caption=u"Display name"
                    description=u"Name shown in tables etc. and on the page"
                ),
                TimestampEditor(
                    name=u"StartTimeOffset",
                    caption=u"Valid from",
                    description=u"Date after which the schedule should be in effect"
                ),
                TimestampEditor(
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
    ),
    u"broadcasts": VirtualTable(u"Broadcast database", Broadcast, 
        EditorTable(
            IDEditorGroup(u"Basic information",
                SelectEditor(
                    name=u"Type",
                    description=u"The broadcast type. This must be data if transmissions are assigned",
                    items=[
                        (u"continous", u"Continous (e.g. Channel marker)", lambda bc: bc.Transmissions.count() == 0),
                        (u"data", u"Data broadcast (i.e. containing transmissions)", True)
                    ]
                ),
                CheckBoxEditor(
                    name=u"Confirmed",
                    caption=u"Confirmed",
                    description=u"Whether the broadcast is confirmed to have taken place"
                ),
                TextAreaEditor(
                    name=u"Comment",
                    caption=u"Comment",
                    description=u"Any comment?"
                )
            ),
            EditorGroup(u"Timing and schedule",
                TimestampEditor(
                    name=u"BroadcastStart",
                    caption=u"Starts at",
                    description=u"Time at which the broadcast started (UTC)",
                ),
                TimestampEditor(
                    name=u"BroadcastEnd",
                    caption=u"Ends at",
                    description=u"Time at which the broadcast ended (UTC)"
                ),
                InputEditor(
                    name=u"ScheduleLeafID",
                    caption=u"Schedule association ID",
                    description=u"Identifies this broadcast as created by a schedule",
                    disabled=True
                )
            )
        ),
        relatedTables=(
            ReferenedVirtualTable(u"stations", match=Broadcast.Station),
            ReferencingVirtualTable(u"transmission", match=Transmission.Broadcast)
        )
    ),
    u"transmissions": VirtualTable(u"Transmission database", Transmission,
        EditorTable(
            IDEditorGroup(u"Basic information",
                TimestampEditor(
                    name=u"Timestamp",
                    description=u"Timestamp at which the transmission started"
                ),
                ForeignEditor(
                    name=u"Callsign",
                    foreignAttribute=u"ForeignCallsign",
                    description=u"The callsign used in the transmission (see priyom.org callsign policies for a reference)"
                ),
                SelectStormObjectEditor(
                    name=u"Class",
                    description=u"Transmission format class; This defines the format of the contents of the transmission",
                    disabled=lambda tx: len(tx.blocks) > 0
                )
            ),
            EditorGroup(u"Media",
                InputEditor(
                    name=u"RecordingURL",
                    description=u"URL referencing a recording if the transmission. Should be on priyom.org domain"
                ),
                TextAreaEditor(
                    name=u"Remarks",
                    description=u"Any remarks about the transmission (like voice sex etc.)"
                )
            )
        )
    )
}
