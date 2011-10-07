# encoding=utf-8
"""
File name: SubmitEvent.py
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
from storm.locals import *
from WebStack.Generic import ContentType, EndOfResponse
from Resource import Resource
from libPriyom import *
from datetime import datetime, timedelta


class SubmitEventResource(Resource):
    def __init__(self, model):
        super(SubmitEventResource, self).__init__(model)
        self.allowedMethods = frozenset(("GET", "POST"))
        
    def insert(self):
        return False
    
    def handle(self, trans):
        trans.set_content_type(ContentType(self.xhtmlContentType, self.encoding))
        
        error = u""
        
        station = self.store.get(Station, self.getQueryValue("stationId", int, default=0))
        startTime = self.getQueryValue("startTime", self.model.PriyomTimestamp(), default=TimeUtils.now())
        endTime = self.getQueryValue("endTime", self.model.AllowBoth(self.model.PriyomTimestamp(allowNone=True), self.model.EmptyString()), defaultKey=u"")
        if endTime == u"":
            endTime = None
        
        print >>self.out, u"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>{1}</title>
        <link rel="stylesheet" type="text/css" href="{0}{2}" />
    </head>
    <body>""".format(
            self.model.rootPath(u""),
            self.model.formatHTMLTitle(u"Submit events"),
            u"/css/submit.css",
        ).encode(self.encoding, 'replace')
        
        submitted = False
        if "submit" in self.query:
            insertResult = self.insert()
            if insertResult is not None:
                error = insertResult
            else:
                submitted = True
                
        if not submitted:
            print >>self.out, u"""
        <form name="logform" method="POST">
            <pre>{0}</pre>
            {1}
            <div class="section">
                <div class="inner-caption">Event information</div>
                Station: <select name="stationId">
                    {2}
                </select><br />
                Event class: <select name="eventClassId">
                    <option value="0">Raw event (see note 2 below)</option>
                    {6}
                </select><br />
                Start time: <input type="text" name="startTime" value="{3}" /><br />
                End time: <input type="text" name="endTime" value="{4}" /> (leave blank if this event is a single point in the time axis; see also the note 1 below)<br />
            </div>
            <div class="section">
                <div class="inner-caption">Description</div>
                <textarea rows="5">{5}</textarea>
            </div>
            <input type="submit" name="submit" value="Submit" />
        </form>"""
        
        print >>self.out, u"""
    </body>
</html>""".encode(self.encoding, 'replace')
