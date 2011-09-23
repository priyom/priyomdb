from WebStack.Generic import ContentType
from libPriyom import *
from API import API, CallSyntax, Argument
import time
from datetime import datetime, timedelta

class TransmissionsByYearAPI(API):
    title = u"getTransmissionsByYear"
    shortDescription = u"list the transmissions of a given calendar year"
    
    docArgs = [
        Argument(u"stationId", u"station id", u"select the station at which to look", metavar="stationid"),
        Argument(u"year", u"integer year", u"year to look at", metavar="year")
    ]
    docCallSyntax = CallSyntax(docArgs, u"?{0}&{1}")
    

    def handle(self, trans):
        stationId = self.getQueryInt("stationId", "must be integer")
        year = self.getQueryInt("year", "must be integer")
            
        lastModified, transmissions = self.priyomInterface.getTransmissionsByMonth(stationId, year, None, limiter=None, notModifiedCheck=self.autoNotModified, head=self.head)
        
        trans.set_header_value('Last-Modified', self.model.formatHTTPTimestamp(float(lastModified)))
        trans.set_content_type(ContentType('application/xml', self.encoding))
        if self.head:
            return
        
        print >>self.out, self.model.exportListToXml(transmissions, Transmission, encoding=self.encoding)

