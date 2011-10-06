"""
File name: WebStackResource.py
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
from WebStack.Resources.ResourceMap import MapResource
from WebStack.Resources.Static import FileResource
from WebStack.Generic import ContentType

from APIDatabase import APICapability
from WebModel import WebModel
import libPriyom
from Resources import *
from Resources.API import *
from Selectors import *
import libPriyom.Plots as Plots
import libPriyom.PlotDataSources as PlotDataSources
import os.path

def intOrNone(str):
    if str.lower() == "none":
        return None
    else:
        return int(str)
    

from cfg_priyomhttpd import application, response
#from Resources.API.FindStations import FindStations
#from Resources.API.FindBroadcasts import FindBroadcasts
#from Resources.API.FindTransmissions import FindTransmissions
#from Resources.API.UpcomingBroadcasts import UpcomingBroadcasts

def get_site_map(priyomInterface):
    rootPath = application["root"]
    
    model = WebModel(priyomInterface)
    
    apiMap = MapSelector("calls", {
        "getUpcomingBroadcasts": UpcomingBroadcastsAPI(model),
        "import": AuthorizationSelector(ImportAPI(model), "transaction"),
        "listStations": ListAPI(model, libPriyom.Station),
        "listBroadcasts": AuthorizationSelector(ListAPI(model, libPriyom.Broadcast, "list"), "list"),
        "listTransmissionClasses": ListAPI(model, libPriyom.TransmissionClass),
        "listTransmissions": AuthorizationSelector(ListAPI(model, libPriyom.Transmission, "list"), "list"),
        "listModulations": ListModulationsAPI(model),
        "getSession": SessionAPI(model),
        "getTransmissionStats": TransmissionStatsAPI(model),
        "getTransmissionsByMonth": TransmissionsByMonthAPI(model),
        "getCloseBroadcasts": CloseBroadcastsAPI(model),
        "getStationFrequencies": StationFrequenciesAPI(model),
        "instanciateSchedules": AuthorizationSelector(InstanciateSchedulesAPI(model), "instanciate"),
        "getTransmissionsByYear": TransmissionsByYearAPI(model),
        "getDuplicatedTransmissionItems": DuplicatedTransmissionItemsAPI(model),
        "plot": MapSelector("plots", {
            "station": MapSelector("station", {
                "hourWeekPunchCard": PlotAPI(model, 
                    PlotDataSources.PlotDataWeekHourPunch(model.store), 
                    Plots.PlotPunchCard(), 
                    [
                        ("stationId", int, "stationId")
                    ],
                    u"punchcard-hw"),
                "hourMonthPunchCard": PlotAPI(model, 
                    PlotDataSources.PlotDataMonthHourPunch(model.store), 
                    Plots.PlotPunchCard(), 
                    [
                        ("stationId", int, "stationId")
                    ],
                    u"punchcard-mw"),
                "hourWeekColourCard": PlotAPI(model, 
                    PlotDataSources.PlotDataWeekHourPunch(model.store), 
                    Plots.PlotColourCard(), 
                    [
                        ("stationId", int, "stationId")
                    ],
                    u"colourcard-hw",
                    subdivision=32,
                    levels=23,
                    mirrored=2),
                "hourMonthColourCard": PlotAPI(model, 
                    PlotDataSources.PlotDataMonthHourPunch(model.store), 
                    Plots.PlotColourCard(), 
                    [
                        ("stationId", int, "stationId")
                    ],
                    u"colourcard-mw",
                    subdivision=32,
                    levels=23,
                    mirrored=2)
            }),
            "uptime": PlotAPI(model,
                PlotDataSources.PlotDataUptime(model.store),
                Plots.PlotStackedGraph(),
                [
                    ("years", WebModel.rangeChecked(int, 1, 10), "years", 5)
                ],
                u"uptime",
                years=5)
        })
    })
    apiMap.mapping[""] = apiMap
    
    return ContinueSelector(
        CompressionSelector(
            ExceptionSelector(
                ResetSelector(model, AuthenticationSelector(model.store, MapSelector("API root", {
                    "station": StationResource(model),
                    "broadcast": IDResource(model, libPriyom.Broadcast),
                    "transmission": IDResource(model, libPriyom.Transmission),
                    "transmissionClass": IDResource(model, libPriyom.TransmissionClass),
                    "schedule": IDResource(model, libPriyom.Schedule),
                    "submit": AuthorizationSelector(SubmitLogResource(model), ["log", "log-moderated"]),
                    "call": apiMap,
                    "doc": DocumentationSelector(apiMap),
                    "": HomeResource(model),
                    "css": MapResource({
                        "home.css": FileResource(os.path.join(rootPath, "www-files/css/home.css"), ContentType("text/css", "utf-8")),
                        "error.css": FileResource(os.path.join(rootPath, "www-files/css/error.css"), ContentType("text/css", "utf-8")),
                        "submit.css": FileResource(os.path.join(rootPath, "www-files/css/submit.css"), ContentType("text/css", "utf-8"))
                    }),
                    "js": MapResource({
                        "jquery.js": FileResource(os.path.join(rootPath, "www-files/js/jquery.js"), ContentType("text/javascript", "utf-8"))
                    })
                }))),
                show = response["showExceptions"]
            )
        )
    )
