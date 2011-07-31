from WebStack.Resources.ResourceMap import MapResource
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from WebStack.Resources.Login import LoginResource, LoginAuthenticator
from WebStack.Resources.Selectors import EncodingSelector, PathSelector

from WebModel import WebModel
from Resources import *
#from Resources.API.FindStations import FindStations
#from Resources.API.FindBroadcasts import FindBroadcasts
#from Resources.API.FindTransmissions import FindTransmissions
#from Resources.API.UpcomingBroadcasts import UpcomingBroadcasts

def get_site_map(priyomInterface):
    model = WebModel(priyomInterface)
    return EncodingSelector(
        MapResource({
            "station": StationResource(model),
            "broadcast": BroadcastResource(model),
            "": EmptyResource(model)
        }),
        "utf-8"
    )
