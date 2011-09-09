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
            
        
        lastModified, broadcasts = self.priyomInterface.getCloseBroadcasts(stationId, time, jitter, self.head)
        trans.set_content_type(ContentType("application/xml"))
        trans.set_header_value("Last-Modified", self.model.formatHTTPTimestamp(lastModified))
        if self.head:
            return
        
        print >>self.out, self.model.exportListToXml(broadcasts, Broadcast)
        
