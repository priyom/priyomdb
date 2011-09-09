from WebStack.Generic import ContentType
from libPriyom import *
from API import API
from ...limits import queryLimits
import time
from datetime import datetime, timedelta

class UpcomingBroadcastsAPI(API):
    def handle(self, trans):
        super(UpcomingBroadcastsAPI, self).handle(trans)
        stationId = self.getQueryIntDefault("stationId", None, "must be integer")
        
        maxTimeRange = queryLimits.broadcasts.maxTimeRangeForUpdatingQueries if stationId is None else queryLimits.broadcasts.maxTimeRangeForStationBoundUpdatingQueries
        
        update = not ("no-update" in self.query)
        all = "all" in self.query
        timeLimit = self.getQueryIntDefault("timeLimit", maxTimeRange, "must be integer")
        if stationId is not None:
            station = self.store.get(Station, stationId)
            if station is None:
                self.parameterError("stationId", "Station does not exist")
        else:
            station = None
            
        lastModified, broadcasts = self.priyomInterface.getUpcomingBroadcasts(station, all, update, timeLimit, maxTimeRange, limiter=self.model, notModifiedCheck=self.autoNotModified, head=self.head)
        if lastModified is None:
            lastModified = self.priyomInterface.now()
        trans.set_content_type(ContentType("application/xml"))
        trans.set_header_value("Last-Modified", self.model.formatHTTPTimestamp(float(lastModified)))
        if self.head:
            return
        broadcasts.order_by(Asc(Broadcast.BroadcastStart))
        
        print >>self.out, self.model.exportListToXml(broadcasts, Broadcast)
