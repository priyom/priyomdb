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
            
        lastModified, transmissions = self.priyomInterface.getTransmissionsByMonth(stationId, year, month, None, self.head)
        
        trans.set_header_value('Last-Modified', self.model.formatHTTPTimestamp(float(lastModified)))
        trans.set_content_type(ContentType('application/xml'))
        if self.head:
            return
        
        print >>self.out, self.model.exportListToXml(transmissions, Transmission)

