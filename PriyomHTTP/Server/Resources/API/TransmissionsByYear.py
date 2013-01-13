"""
File name: TransmissionsByYear.py
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
from PriyomHTTP.Server.Resources.API.API import API, CallSyntax, Argument

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

        if lastModified is not None:
            trans.set_header_value('Last-Modified', self.model.formatHTTPTimestamp(float(lastModified)))
        trans.set_content_type(ContentType('application/xml', self.encoding))
        if self.head:
            return

        self.model.exportListToFile(self.out, transmissions, Transmission, encoding=self.encoding, flags={"with-freqs"})

