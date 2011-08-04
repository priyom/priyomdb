from WebStack.Resources.ResourceMap import MapResource
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from WebStack.Resources.Login import LoginResource, LoginAuthenticator
from WebStack.Resources.Selectors import EncodingSelector, PathSelector

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
    
    apiMap = MapResource({
        "getUpcomingBroadcasts": UpcomingBroadcastsAPI(model)
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
