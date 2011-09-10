from WebStack.Generic import ContentType
from libPriyom import *
from API import API

class StationFrequenciesAPI(API):
    def __init__(self, model):
        super(StationFrequenciesAPI, self).__init__(model)
    
    def handle(self, trans):
        super(StationFrequenciesAPI, self).handle(trans)
        stationId = self.getQueryInt("stationId", "must be integer")
        station = self.store.get(Station, stationId)
        if station is None:
            self.parameterError("stationId", "Station does not exist")
        
        lastModified, frequencies = self.priyomInterface.getStationFrequencies(station, notModifiedCheck=self.autoNotModified, head=self.head)
        trans.set_content_type(ContentType("application/xml"))
        trans.set_header_value("Last-Modified", self.model.formatHTTPTimestamp(lastModified))
        if self.head:
            return
        
        print >>self.out, self.model.exportListToXml(broadcasts, Broadcast)


