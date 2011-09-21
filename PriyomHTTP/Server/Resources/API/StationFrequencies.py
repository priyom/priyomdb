from WebStack.Generic import ContentType
from libPriyom import *
from API import API, CallSyntax, Argument
from libPriyom.Interface import PAST, ONAIR, UPCOMING

class StationFrequenciesAPI(API):
    title = u"getStationFrequencies"
    shortDescription = u"get a list of frequencies the station uses"
    
    docArgs = [
        Argument(u"stationId", u"station id", u"select the station at which to look", metavar="stationid")
    ]
    docCallSyntax = CallSyntax(docArgs, u"?{0}")
    
    def handle(self, trans):
        stationId = self.getQueryInt("stationId", "must be integer")
        station = self.store.get(Station, stationId)
        if station is None:
            self.parameterError("stationId", "Station does not exist")
        
        lastModified, frequencies = self.priyomInterface.getStationFrequencies(station, notModifiedCheck=self.autoNotModified, head=self.head)
        trans.set_content_type(ContentType("application/xml", self.encoding))
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
        
        print >>self.out, doc.toxml(encoding=self.encoding)


