"""
File name: InstanciateSchedules.py
This file is part of: priyomdb

LICENSE

The contents of this file are subject to the Mozilla Public License
Version 1.1 (the "License"); you may not use this file except in
compliance with the License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/

Software distributed under the License is distributed on an "AS IS"
basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
License for the specific language governing rights and limitations under
the License.

Alternatively, the contents of this file may be used under the terms of
the GNU General Public license (the  "GPL License"), in which case  the
provisions of GPL License are applicable instead of those above.

FEEDBACK & QUESTIONS

For feedback and questions about priyomdb please e-mail one of the
authors:
    Jonas Wielicki <j.wielicki@sotecware.net>
"""
from WebStack.Generic import ContentType
import time
from datetime import datetime, timedelta

from libPriyom import *
from libPriyom.Formatting import priyomdate

from PriyomHTTP.Server.limits import queryLimits
from PriyomHTTP.Server.Resources.API.API import API, CallSyntax, Argument

class InstanciateSchedulesAPI(API):
    title = u"instanciateSchedules"
    shortDescription = u"instanciate schedules"
    
    docArgs = [
        Argument(u"stationId", u"station ID", u"Restrict the instanciation to a single station", metavar="stationid", optional=True),
    ]
    docCallSyntax = CallSyntax(docArgs, u"?{0}")
    docRequiredPrivilegues = u"instanciate"
    
    def __init__(self, model):
        super(InstanciateSchedulesAPI, self).__init__(model)
        self.allowedMethods = frozenset(("POST", "GET", "HEAD"))
    
    def handle(self, trans):
        stationId = self.getQueryIntDefault("stationId", None, "must be integer")
        
        trans.set_content_type(ContentType("text/plain", self.encoding))
        if self.head:
            return
        if trans.get_request_method() == "GET":
            print >>self.out, u"failed: Call this resource with POST to perform instanciation.".encode(self.encoding)
            return
        
        generatedUntil = 0
        if stationId is None:
            generatedUntil = self.priyomInterface.scheduleMaintainer.updateSchedules(None)
        else:
            generatedUntil = self.priyomInterface.scheduleMaintainer.updateSchedule(self.store.get(Station, stationId), None)
        
        print >>self.out, u"success: valid until {0}".format(datetime.fromtimestamp(generatedUntil).strftime(priyomdate)).encode(self.encoding)

