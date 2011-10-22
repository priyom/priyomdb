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
from libPriyom import *
from datetime import datetime, timedelta
from SubmitResource import SubmitResource, SubmitParameterError
from xml.sax.saxutils import escape
from Types import Typecasts

class SubmitEventResource(SubmitResource):
    def __init__(self, model):
        super(SubmitEventResource, self).__init__(model)
        self.allowedMethods = frozenset(("GET", "POST"))
        
        self.startTimeTypecast = Typecasts.PriyomTimestamp()
        self.endTimeTypecast = Typecasts.AllowBoth(
            Typecasts.PriyomTimestamp(),
            Typecasts.EmptyString()
        )
        
    def _eventInformationTree(self, parent):
        parent[0].tail = u"Station: "
        self._stationSelect(parent, name=u"station", value=self.station)
        
        self.br(parent, u"Event class: ")
        eventClassSelect = self.SubElement(parent, u"select", name=u"eventClass")
        self.SubElement(eventClassSelect, u"option", value=u"").text = u"Raw event (see note 2)"
        
        for eventClass in self.store.find(EventClass):
            option = self.SubElement(eventClassSelect, u"option", value=unicode(eventClass.ID))
            option.text = unicode(eventClass)
            if eventClass is self.eventClass:
                option.set(u"selected", u"selected")
        
        self.br(parent, u"Start time: ")
        self.input(parent, name=u"startTime", value=self.startTime.strftime(Formatting.priyomdate))
        
        self.br(parent, u"End time: ")
        self.input(parent, name=u"endTime", value=self.endTime.strftime(Formatting.priyomdate) if self.endTime is not None else u"").tail = u" (leave blank if this event is a single point in the time axis; see also the note 1 below)"
        
    def _descriptionTree(self, parent):
        self.SubElement(parent, u"textarea", rows=u"7", name=u"description").text = self.description
        
    def _noteTree(self, parent):
        ol = self.SubElement(parent, u"ol")
        li = self.SubElement(ol, u"li")
        self.SubElement(li, u"p").text = u"Note that for events which indicate state changes, there is no need to create two separate events to indicate start and ending. If the event class is “state changing” (its indicated in its name if so), two separate events will automatically be generated in any event listing output. These will be prefixed with “Start of” and “End of” respectively."
        self.SubElement(li, u"p").text = u"If the endTime is omitted, “Start of” is left out on the first and only event."
        
        li = self.SubElement(ol, u"li")
        self.SubElement(li, u"p").text = u"A raw event is any event which does not fit in any event class. Try to keep the description structured though, in case we want to merge these events to a common event class later. Watch out for existing events having similar contents before submitting."
        
    def insert(self):
        self.station = self.getQueryValue("station", Typecasts.validStormObject(Station, self.store))
        
        if self.error is not None:
            self.setError(self.error)
            
        event = Event()
        try:
            event.Station = self.station
            event.StartTime = TimeUtils.toTimestamp(self.startTime)
            event.EndTime = TimeUtils.toTimestamp(self.endTime) if self.endTime is not None else None
            event.Description = self.description
            event.EventClass = self.eventClass
        except BaseException as e:
            del event
            self.setError(unicode(e))
        self.store.add(event)
        self.store.commit()
        
        self.SubElement(self.body, u"pre").text = u"""Added new event
Station: {0}
Event (#{2}): {1}""".format(
            unicode(event.Station),
            unicode(event),
            unicode(event.ID)
        )
    
    def buildDoc(self, trans, elements):
        super(SubmitEventResource, self).buildDoc(trans, elements)
        
        self.station = self.getQueryValue("station", Typecasts.ValidStormObject(Station, self.store), defaultKey=None)
        self.eventClass = self.getQueryValue("eventClass", Typecasts.AllowBoth(Typecasts.ValidStormObject(EventClass, self.store), Typecasts.EmptyString()), defaultKey=None)
        if self.eventClass == u"":
            self.eventClass = None
        self.startTime = self.getQueryValue("startTime", Typecasts.PriyomTimestamp(), defaultKey=TimeUtils.nowDate())
        self.endTime = self.getQueryValue("endTime", Typecasts.AllowBoth(Typecasts.PriyomTimestamp(), Typecasts.EmptyString()), defaultKey=None)
        if self.endTime == u"":
            self.endTime = None
        self.description = self.query.get("description", u"")
        if len(self.description) < 10:
            self.error = u"Description must be at least 10 characters long."
        
        self.link(u"/css/submit.css")
        self.setTitle(u"Submit event")
        
        submitted = False
        if "submit" in self.query and self.error is None:
            try:
                self.insert()
                submitted = True
            except SubmitParameterError:
                submitted = False
            
        
        if not submitted:
            self.SubElement(self.body, u"pre").text = self.recursiveDict(self.query)
            if self.error is not None:
                self.SubElement(self.body, u"div", attrib={
                    u"class": u"error"
                }).text = self.error
                
            form = self.SubElement(self.body, u"form", name=u"logform", method=u"POST")
            
            self._eventInformationTree(self.section(form, u"Event information"))
            self._descriptionTree(self.section(form, u"Description"))
            
            self.input(form, type=u"submit", name=u"submit", value=u"Submit")
            
            self._noteTree(self.section(self.body, u"Notes"))
            
