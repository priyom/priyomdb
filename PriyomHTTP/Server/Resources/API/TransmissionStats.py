from WebStack.Generic import ContentType
from libPriyom import *
from API import API, CallSyntax, Argument
import time
from datetime import datetime, timedelta

class TransmissionStatsAPI(API):
    title = u"getTransmissionStats"
    shortDescription = u"get the amount of transmissions grouped by calendar months"
    
    docArgs = [
        Argument(u"stationId", u"station id", u"select the station at which to look", metavar="stationid")
    ]
    docCallSyntax = CallSyntax(docArgs, u"?{0}")
    
    def handle(self, trans):
        stationId = self.getQueryInt("stationId", "must be integer")
        
        lastModified, months = self.priyomInterface.getTransmissionStats(stationId, notModifiedCheck=self.autoNotModified, head=self.head)
        trans.set_content_type(ContentType("application/xml", self.encoding))
        trans.set_header_value('Last-Modified', self.model.formatHTTPTimestamp(float(lastModified)))
        if self.head:
            return
        
        doc = self.model.getExportDoc("transmission-stats")
        rootNode = doc.documentElement
        
        for month in months:
            node = XMLIntf.buildTextElementNS(doc, "transmission-count", str(month[2]), XMLIntf.namespace)
            node.setAttribute("year", str(month[0]))
            node.setAttribute("month", str(month[1]))
            rootNode.appendChild(node)
        
        print >>self.out, doc.toxml(encoding=self.encoding)
