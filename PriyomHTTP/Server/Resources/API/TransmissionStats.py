from WebStack.Generic import ContentType
from libPriyom import *
from API import API
import time
from datetime import datetime, timedelta

class TransmissionStatsAPI(API):
    def handle(self, trans):
        super(TransmissionStatsAPI, self).handle(trans)
        stationId = self.getQueryInt("stationId", "must be integer")
        
        months = self.store.execute("SELECT YEAR(FROM_UNIXTIME(Timestamp)) as year, MONTH(FROM_UNIXTIME(Timestamp)) as month, COUNT(DATE_FORMAT(FROM_UNIXTIME(Timestamp), '%%Y-%%m')) FROM transmissions LEFT JOIN broadcasts ON (transmissions.BroadcastID = broadcasts.ID) WHERE broadcasts.StationID = '%d' GROUP BY year, month ORDER BY year ASC, month ASC" % (stationId))
        
        doc = self.model.getExportDoc("transmission-stats")
        rootNode = doc.documentElement
        
        for month in months:
            node = XMLIntf.buildTextElementNS(doc, "transmission-count", str(month[2]), XMLIntf.namespace)
            node.setAttribute("year", str(month[0]))
            node.setAttribute("month", str(month[1]))
            rootNode.appendChild(node)
        
        trans.set_content_type(ContentType("text/xml"))
        print >>self.out, doc.toxml()
