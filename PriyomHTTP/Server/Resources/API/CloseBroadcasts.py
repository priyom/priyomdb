from WebStack.Generic import ContentType
from libPriyom import *
from API import API

class CloseBroadcastsAPI(API):
    def __init__(self, model):
        super(CloseBroadcastsAPI, self).__init__(model)
    
    def handle(self, trans):
        super(CloseBroadcastsAPI, self).handle(trans)
        
        stationId = self.getQueryInt("stationId", "int; id of the station")
        time = self.getQueryInt("time", "int; unix timestamp at which to look")
        jitter = self.getQueryIntDefault("jitter", 600, "int; jitter in seconds")
        if jitter < 0 or jitter > 600:
            self.parameterError("jitter", "jitter %d out of bounds (0..600)" % (jitter))
            
        
        wideBroadcasts = self.store.find(Broadcast, Broadcast.StationID == stationId)
        lastModified = wideBroadcasts.max(Broadcast.Modified)
        
        broadcasts = wideBroadcasts.select(And(
                    Broadcast.BroadcastStart <= time + jitter,
                    Broadcast.BroadcastEnd > time - jitter
                ))
        print(list(broadcasts))
        
        
