"""
File name: CloseBroadcasts.py
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
from libPriyom import *
from API import API, CallSyntax, Argument

class CloseBroadcastsAPI(API):
    title = u"getCloseBroadcasts"
    shortDescription = u"Find broadcasts close to a given timestamp"
    
    docArgs = [
        Argument(u"stationId", u"station ID", u"id of the station at which to search for broadcasts", metavar=u"stationid"),
        Argument(u"time", u"unix timestamp", u"center of the time area which to take into account", metavar=u"timestamp"),
        Argument(u"jitter", u"seconds", u"amount of seconds to look around the given timestamp. defaults to 600 seconds", metavar=u"seconds", optional=True)
    ]
    docCallSyntax = CallSyntax(docArgs, u"?{0}&{1}&{2}")
    
    def handle(self, trans):
        stationId = self.getQueryInt("stationId", "int; id of the station")
        time = self.getQueryInt("time", "int; unix timestamp at which to look")
        jitter = self.getQueryIntDefault("jitter", 600, "int; jitter in seconds")
        if jitter < 0 or jitter > 600:
            self.parameterError("jitter", "jitter %d out of bounds (0..600)" % (jitter))
            
        
        lastModified, broadcasts = self.priyomInterface.getCloseBroadcasts(stationId, time, jitter, notModifiedCheck=self.autoNotModified, head=self.head)
        trans.set_content_type(ContentType("application/xml", self.encoding))
        trans.set_header_value("Last-Modified", self.model.formatHTTPTimestamp(lastModified))
        if self.head:
            return
        
        self.model.exportListToFile(self.out, broadcasts, Broadcast, encoding=self.encoding)
        
