from WebStack.Generic import ContentType
from libPriyom import *
from API import API
import time
from datetime import datetime, timedelta

class TransmissionsByMonthAPI(API):
    def handle(self, trans):
        super(TransmissionsByMonthAPI, self).handle(trans)
        stationId = self.getQueryInt("stationId", "must be integer")
        year = self.getQueryInt("year", "must be integer")
        month = self.getQueryInt("month", "must be integer")
        if month < 1 or month > 12:
            self.parameterError("month", "Month %d out of bounds (1..12)" % (month))
            return
        
        startTimestamp = datetime(year, month, 1)
        if month != 12:
            endTimestamp = datetime(year, month+1, 1)
        else:
            endTimestamp = datetime(year+1, 1, 1)
        startTimestamp = int(time.mktime(startTimestamp.timetuple()))
        endTimestamp = int(time.mktime(endTimestamp.timetuple()))
        
        transmissions = self.store.find((Transmission, Broadcast), 
            Transmission.BroadcastID == Broadcast.ID,
            And(Broadcast.StationID == stationId, 
                And(Transmission.Timestamp >= startTimestamp,
                    Transmission.Timestamp < endTimestamp)))
        lastModified = transmissions.max(Transmission.Modified)
        
        trans.set_header_value('Last-Modified', self.model.formatHTTPTimestamp(float(lastModified)))
        trans.set_content_type(ContentType('application/xml'))
        if trans.get_request_method() == 'HEAD':
            return
        
        print >>self.out, self.model.exportListToXml((transmission for (transmission, broadcast) in transmissions), Transmission)

