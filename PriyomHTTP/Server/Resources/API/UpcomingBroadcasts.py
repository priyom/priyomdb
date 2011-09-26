"""
File name: UpcomingBroadcasts.py
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
# encoding=utf-8
from WebStack.Generic import ContentType
from libPriyom import *
from API import API, CallSyntax, Argument
from ...limits import queryLimits
import time
from datetime import datetime, timedelta

class UpcomingBroadcastsAPI(API):
    title = u"getUpcomingBroadcasts"
    shortDescription = u"Returns a list of upcoming broadcasts"
    
    docArgs = [
        Argument(u"stationId", u"station ID", u"Restrict the lookup to a single station", metavar="stationid", optional=True),
        Argument(u"timeLimit", u"integer seconds", u"How many seconds to look into the future. This is constrained depending on the other parameters.", metavar="seconds", optional=True),
        Argument(u"all", u"", "If given, even non-data broadcasts will be shown.", optional=True),
        Argument(u"no-update", u"", "If given, no update of schedules is performed (may result in outdated data, reduces server load).", optional=True)
    ]
    docCallSyntax = CallSyntax(docArgs, u"?{0}&{1}&{2}&{3}")
    
    def handle(self, trans):
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
            
        lastModified, broadcasts, upToDate, validUntil = self.priyomInterface.getUpcomingBroadcasts(station, all, update, timeLimit, maxTimeRange, limiter=self.model, notModifiedCheck=self.autoNotModified, head=self.head)
        trans.set_content_type(ContentType("application/xml", self.encoding))
        if lastModified is not None:
            trans.set_header_value("Last-Modified", self.model.formatHTTPTimestamp(float(lastModified)))
        if self.head:
            return
        if not upToDate:
            trans.set_header_value("Warning", """199 api.priyom.org "Currently not all upcoming broadcasts from all affected schedules are instanciated up to date. Maybe your timeLimit is too high for this to ever happen" """)
        broadcasts.order_by(Asc(Broadcast.BroadcastStart))
        
        doc = self.model.exportListToDom(broadcasts, Broadcast, flags=frozenset())
        doc.documentElement.setAttribute("valid-until", unicode(long(validUntil)))
        print >>self.out, doc.toxml(self.encoding)
