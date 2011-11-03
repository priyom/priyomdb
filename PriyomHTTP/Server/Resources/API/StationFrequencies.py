"""
File name: StationFrequencies.py
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
from libPriyom.Interface import PAST, ONAIR, UPCOMING

class StationFrequenciesAPI(API):
    title = u"getStationFrequencies"
    shortDescription = u"get a list of frequencies the station uses"
    
    docArgs = [
        Argument(u"stationId", u"station id", u"select the station at which to look", metavar="stationid")
    ]
    docCallSyntax = CallSyntax(docArgs, u"?{0}")
    
    def handle(self, trans):
        stationId = self.getQueryInt("stationId", "must be integer")
        station = self.store.get(Station, stationId)
        if station is None:
            self.parameterError("stationId", "Station does not exist")
        
        lastModified, frequencies = self.priyomInterface.getStationFrequencies(station, notModifiedCheck=self.autoNotModified, head=self.head)
        trans.set_content_type(ContentType("application/xml", self.encoding))
        trans.set_header_value("Last-Modified", self.model.formatHTTPTimestamp(lastModified))
        if self.head:
            return
        
        doc = self.model.getExportTree("station-frequencies")
        rootNode = doc.getroot()
        
        for (freq, modulation, state, timestamp) in frequencies:
            node = XMLIntf.appendTextElement(rootNode, u"station-frequency", unicode(freq), attrib={
                u"modulation": modulation,
                u"state": state
            })
            if state != ONAIR:
                node.set(u"unix", unicode(timestamp))
        
        self.model.etreeToFile(self.out, doc, encoding=self.encoding)


