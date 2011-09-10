from WebStack.Generic import ContentType
from libPriyom import *
from API import API
from libPriyom.Interface import PAST, ONAIR, UPCOMING

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
        
        doc = self.model.getExportDoc("station-frequencies")
        rootNode = doc.documentElement
        
        for (freq, modulation, state, timestamp) in frequencies:
            node = XMLIntf.buildTextElementNS(doc, "station-frequency", unicode(freq), XMLIntf.namespace)
            node.setAttribute("modulation", modulation)
            node.setAttribute("state", state)
            if state != ONAIR:
                node.setAttribute("unix", unicode(timestamp))
            rootNode.appendChild(node)
        
        print >>self.out, doc.toxml()


