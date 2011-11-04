"""
File name: Station.py
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
from libPriyom import *
from WebStack.Generic import ContentType, EndOfResponse
from PriyomHTTP.Server.Resources.Resource import Resource

class StationResource(Resource):
    def __init__(self, model):
        super(StationResource, self).__init__(model)
        
    def handle(self, trans):
        path = trans.get_virtual_path_info().split('/')
        if len(path) == 1:
            trans.set_response_code(404)
            return
        elif len(path) > 2:
            trans.set_response_code(404)
            return
        
        stationDesignator = path[1].decode("utf-8")
        if len(stationDesignator) == 0:
            return None
        (lastModified, station) = self.priyomInterface.getStation(stationDesignator, notModifiedCheck=self.autoNotModified)
        if station is None:
            trans.set_response_code(404)
            return
        
        trans.set_header_value("Last-Modified", self.model.formatHTTPTimestamp(lastModified))
        trans.set_content_type(ContentType("application/xml", self.encoding))
        self.model.exportToFile(self.out, station, encoding=self.encoding)

