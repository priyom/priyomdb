from WebStack.Resources.ResourceMap import MapResource
from WebStack.Resources.Static import FileResource
from WebStack.Generic import ContentType

from APIDatabase import APICapability
from WebModel import WebModel
import libPriyom
from Resources import *
from Resources.API import *
from Selectors import *
import os.path

from cfg_priyomhttpd import application, response
#from Resources.API.FindStations import FindStations
#from Resources.API.FindBroadcasts import FindBroadcasts
#from Resources.API.FindTransmissions import FindTransmissions
#from Resources.API.UpcomingBroadcasts import UpcomingBroadcasts

def get_site_map(priyomInterface):
    rootPath = application["root"]
    
    model = WebModel(priyomInterface)
    
    apiMap = MapResource({
        "getUpcomingBroadcasts": UpcomingBroadcastsAPI(model),
        "import": AuthorizationSelector(ImportAPI(model), "transaction"),
        "listStations": ListAPI(model, libPriyom.Station),
        "listBroadcasts": AuthorizationSelector(ListAPI(model, libPriyom.Broadcast), "list"),
        "listTransmissionClasses": ListAPI(model, libPriyom.TransmissionClass),
        "listTransmissions": AuthorizationSelector(ListAPI(model, libPriyom.Transmission), "list"),
        "listModulations": ListModulationsAPI(model),
        "getSession": SessionAPI(model),
        "getTransmissionStats": TransmissionStatsAPI(model),
        "getTransmissionsByMonth": TransmissionsByMonthAPI(model),
        "getCloseBroadcasts": CloseBroadcastsAPI(model),
        "getStationFrequencies": StationFrequenciesAPI(model)
    })
    
    return ContinueSelector(
        CompressionSelector(
            ExceptionSelector(
                ResetSelector(model, AuthenticationSelector(model.store, MapResource({
                    "station": StationResource(model),
                    "broadcast": IDResource(model, libPriyom.Broadcast),
                    "transmission": IDResource(model, libPriyom.Transmission),
                    "transmissionClass": IDResource(model, libPriyom.TransmissionClass),
                    "schedule": IDResource(model, libPriyom.Schedule),
                    "call": apiMap,
                    "doc": DocumentationSelector(apiMap),
                    "": EmptyResource(model),
                    "css": MapResource({
                        "home.css": FileResource(os.path.join(rootPath, "www-files/css/home.css"), ContentType("text/css", "utf-8")),
                        "error.css": FileResource(os.path.join(rootPath, "www-files/css/error.css"), ContentType("text/css", "utf-8"))
                    })
                }))),
                show = response["showExceptions"]
            )
        )
    )
