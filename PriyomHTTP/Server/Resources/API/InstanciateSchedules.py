from WebStack.Generic import ContentType
from libPriyom import *
from API import API
from ...limits import queryLimits
import time
from datetime import datetime, timedelta

class InstanciateSchedulesAPI(API):
    def __init__(self, model):
        super(InstanciateSchedulesAPI, self).__init__(model)
        self.allowedMethods = frozenset(("POST", "GET", "HEAD"))
    
    def handle(self, trans):
        super(InstanciateSchedulesAPI, self).handle(trans)
        stationId = self.getQueryIntDefault("stationId", None, "must be integer")
        
        trans.set_content_type(ContentType("text/plain", self.encoding))
        if self.head:
            return
        if trans.get_request_method() == "GET":
            print >>self.out, u"Call this resource with POST to perform instanciation.".encode(self.encoding)
            return
        
        generatedUntil = 0
        if stationId is None:
            generatedUntil = self.priyomInterface.scheduleMaintainer.updateSchedules(None)
        else:
            generatedUntil = self.priyomInterface.scheduleMaintainer.updateSchedule(self.store.get(Station, stationId), None)
        
        print >>self.out, u"Schedules generated until {0}".format(datetime.fromtimestamp(self.priyomInterface.now())).encode(self.encoding)

