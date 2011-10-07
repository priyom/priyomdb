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
from .SubmitLog import SubmitLogResource
from xml.sax.saxutils import escape


class SubmitEventResource(Resource):
    def __init__(self, model):
        super(SubmitEventResource, self).__init__(model)
        self.allowedMethods = frozenset(("GET", "POST"))
        
        self.startTimeTypecast = self.model.PriyomTimestamp()
        self.endTimeTypecast = self.model.AllowBoth(
            self.model.PriyomTimestamp(),
            self.model.EmptyString()
        )
        
    def insert(self):
        try:
            station = self.model.validStormObject(Station, self.store)(self.query["stationId"])
            startTime = self.startTimeTypecast(self.query["startTime"])
            endTime = self.endTimeTypecast(self.query["endTime"])
            if endTime == u"":
                endTime = None
            description = self.query["description"]
            if len(description) < 10:
                raise ValueError(u"At least 10 characters of description required")
            eventClass = self.model.validStormObject(EventClass, self.store)(self.query["eventClassId"]) if self.query["eventClassId"] != u"0" else None
        except ValueError as e:
            return unicode(e)
        except KeyError as e:
            return u"missing submit data: {0}".format(unicode(e))
        except TypeError as e:
            return unicode(e)
            
        event = Event()
        try:
            event.Station = station
            event.StartTime = TimeUtils.toTimestamp(startTime)
            event.EndTime = TimeUtils.toTimestamp(endTime) if endTime is not None else None
            event.Description = description
            event.EventClass = eventClass
        except BaseException as e:
            del event
            return unicode(e)
        self.store.add(event)
        
        print >>self.out, u"""<pre>Added new event to station {0}: {1}</pre>""".format(escape(unicode(station)), escape(unicode(event)))
    
    def handle(self, trans):
        trans.set_content_type(ContentType(self.xhtmlContentType, self.encoding))
        
        error = u""
        
        station = self.getQueryValue("stationId", self.model.validStormObject(Station, self.store), default=None)
        startTime = self.getQueryValue("startTime", self.model.PriyomTimestamp(), defaultKey=TimeUtils.nowDate(), default=None)
        endTime = self.getQueryValue("endTime", self.model.AllowBoth(self.model.PriyomTimestamp(), self.model.EmptyString()), defaultKey=u"", default=None)
        description = self.query.get("description", u"")
        
        if startTime is None:
            error = u"Malformatted start time"
            startTime = TimeUtils.nowDate()
        if endTime is None:
            error = u"Malformatted end time"
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
        if "submit" in self.query and len(error) == 0:
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
                <textarea rows="7" cols="100" name="description">{5}</textarea>
            </div>
            <input type="submit" name="submit" value="Submit" />
        </form>""".format(
            SubmitLogResource.recursiveDict(self.query),
            u"" if len(error) == 0 else u"""<div class="error">{0}</div>""".format(escape(error)),
            u"\n                    ".join(
                (u'<option value="{0}"{1}>{2}</option>'.format(tmpstation.ID, u' selected="selected"' if tmpstation is station else u'', escape(unicode(tmpstation))) for tmpstation in self.store.find(Station))
            ),
            startTime.strftime(Formatting.priyomdate),
            endTime.strftime(Formatting.priyomdate) if endTime is not None else u"",
            escape(description),
            u"\n                    ".join(
                (u'<option value="{0}"{1}>{2}</option>'.format(tmpEventClass.ID, u' selected="selected"' if tmpEventClass is eventClass else u'', escape(unicode(tmpEventClass))) for tmpEventClass in self.store.find(EventClass))
            )
        ).encode(self.encoding, 'replace')
        
        print >>self.out, u"""
        <div class="section">
            <div class="inner-caption">Notes</div>
            <ol>
                <li><p>Note that for events which indicate state changes, there is no need to create two separate events to indicate start and ending. If the event class is “state changing” (its indicated in its name if so), two separate events will automatically be generated in any event listing output. These will be prefixed with “Start of” and “End of” respectively.</p>
                <p>If the endTime is omitted, “Start of” is left out on the first and only event.</p></li>
                <li><p>A raw event is any event which does not fit in any event class. Try to keep the description structured though, in case we want to merge these events to a common event class later. Watch out for existing events having similar contents before submitting.</p></li>
            </ol>
        </div>
    </body>
</html>""".encode(self.encoding, 'replace')
