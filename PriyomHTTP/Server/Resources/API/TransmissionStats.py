from WebStack.Generic import ContentType
from libPriyom import *
from API import API
import time
from datetime import datetime, timedelta

class TransmissionStatsAPI(API):
    def handle(self, trans):
        super(TransmissionStatsAPI, self).handle(trans)
        stationId = self.getQueryInt("stationId", "must be integer")
        
        trans.set_content_type(ContentType("application/xml"))
        trans.set_header_value('Last-Modified', self.model.formatHTTPTimestamp(float(lastModified)))
        lastModified, months = self.priyomInterface.getTransmissionStats(stationId, notModifiedCheck=self.autoNotModified, head=self.head)
        if self.head:
            return
        
        doc = self.model.getExportDoc("transmission-stats")
        rootNode = doc.documentElement
        
        for month in months:
            node = XMLIntf.buildTextElementNS(doc, "transmission-count", str(month[2]), XMLIntf.namespace)
            node.setAttribute("year", str(month[0]))
            node.setAttribute("month", str(month[1]))
            rootNode.appendChild(node)
        
        print >>self.out, doc.toxml()
