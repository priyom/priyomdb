from WebStack.Resources.ResourceMap import MapResource
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from WebStack.Resources.Login import LoginResource, LoginAuthenticator
from WebStack.Resources.Selectors import EncodingSelector, PathSelector

from APIDatabase import APICapability
from Authentication import AuthenticationSelector
from WebModel import WebModel
from Documentation import DocumentationSelector
from libPriyom import *
from Resources import *
from Resources.API import *
#from Resources.API.FindStations import FindStations
#from Resources.API.FindBroadcasts import FindBroadcasts
#from Resources.API.FindTransmissions import FindTransmissions
#from Resources.API.UpcomingBroadcasts import UpcomingBroadcasts

def get_site_map(priyomInterface):
    model = WebModel(priyomInterface)
    
    apiCap = model.store.find(APICapability, APICapability.Capability == u"transaction").any()
    if apiCap is None:
        raise Exception("Cannot find API capability \"transaction\".")
    
    apiMap = MapResource({
        "getUpcomingBroadcasts": UpcomingBroadcastsAPI(model),
        "import": AuthenticationSelector(model.store, ImportAPI(model), apiCap)
    })
    
    return EncodingSelector(
        MapResource({
            "station": StationResource(model),
            "broadcast": IDResource(model, Broadcast),
            "transmission": IDResource(model, Transmission),
            "schedule": IDResource(model, Schedule),
            "call": apiMap,
            "doc": DocumentationSelector(apiMap),
            "": EmptyResource(model)
        }),
        "utf-8"
    )
