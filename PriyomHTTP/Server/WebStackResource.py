from WebStack.Resources.ResourceMap import MapResource

from APIDatabase import APICapability
from Authentication import AuthenticationSelector
from Authorization import AuthorizationSelector
from WebModel import WebModel
from Documentation import DocumentationSelector
from Reset import ResetSelector
import libPriyom
from Resources import *
from Resources.API import *
from Encoding import MyEncodingSelector
#from Resources.API.FindStations import FindStations
#from Resources.API.FindBroadcasts import FindBroadcasts
#from Resources.API.FindTransmissions import FindTransmissions
#from Resources.API.UpcomingBroadcasts import UpcomingBroadcasts

def get_site_map(priyomInterface):
    model = WebModel(priyomInterface)
    
    apiMap = MapResource({
        "getUpcomingBroadcasts": UpcomingBroadcastsAPI(model),
        "import": AuthorizationSelector(ImportAPI(model), "transaction"),
        "listStations": ListAPI(model, libPriyom.Station),
        "listBroadcasts": AuthorizationSelector(ListAPI(model, libPriyom.Broadcast), "list"),
        "listTransmissionClasses": ListAPI(model, libPriyom.TransmissionClass),
        "listTransmissions": AuthorizationSelector(ListAPI(model, libPriyom.Transmission), "list"),
        "listModulations": ListModulationsAPI(model),
        "getSession": SessionAPI(model)
    })
    
    return MyEncodingSelector(ResetSelector(model, AuthenticationSelector(model.store,
        MapResource({
            "station": StationResource(model),
            "broadcast": IDResource(model, libPriyom.Broadcast),
            "transmission": IDResource(model, libPriyom.Transmission),
            "transmissionClass": IDResource(model, libPriyom.TransmissionClass),
            "schedule": IDResource(model, libPriyom.Schedule),
            "call": apiMap,
            "doc": DocumentationSelector(apiMap),
            "": EmptyResource(model)
        }))),
        "utf-8"
    )
