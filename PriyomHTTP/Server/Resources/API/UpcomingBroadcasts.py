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
            
        now = self.model.now()
        if update:
            untilDate = datetime.fromtimestamp(now)
            untilDate += timedelta(seconds=timeLimit)
            untilDate = self.model.normalizeDate(untilDate)
            
            until = self.model.toTimestamp(untilDate)
            
            if station is None:
                validUntil = self.priyomInterface.scheduleMaintainer.updateSchedules(until, maxTimeRange)
            else:
                validUntil = self.priyomInterface.scheduleMaintainer.updateSchedule(station, until, maxTimeRange)
            trans.set_header_value("Expires", self.model.formatHTTPTimestamp(validUntil))
        
        where = And(Or(Broadcast.BroadcastEnd > now, Broadcast.BroadcastEnd == None), (Broadcast.BroadcastStart < (now + timeLimit)))
        if not all:
            where = And(where, Broadcast.Type == u"data")
        if stationId is not None:
            where = And(where, Broadcast.StationID == stationId)
            
        resultSet = self.store.find(Broadcast, where)
        resultSet.order_by(Desc(Broadcast.BroadcastStart))
        self.model.limitResults(resultSet)
        
        trans.set_content_type(ContentType("application/xml"))
        print >>self.out, self.model.exportListToXml((broadcast for broadcast in resultSet), Broadcast)
