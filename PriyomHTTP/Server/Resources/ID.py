"""
File name: ID.py
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
from WebStack.Generic import ContentType
from Resource import Resource

class IDResource(Resource):
    def __init__(self, model, classType):
        super(IDResource, self).__init__(model)
        self.classType = classType
        
    def handle(self, trans):
        path = trans.get_virtual_path_info().split('/')
        if len(path) == 1:
            trans.set_response_code(404)
            return
        elif len(path) > 2:
            trans.set_response_code(404)
            return
        
        try:
            objId = int(path[1].decode("utf-8"))
        except ValueError:
            trans.set_response_code(404)
            return
        obj = self.store.get(self.classType, objId)
        if obj is None:
            trans.set_response_code(404)
            return
        obj.validate()
        self.autoNotModified(obj.Modified)
        
        trans.set_header_value("Last-Modified", self.model.formatHTTPTimestamp(obj.Modified))
        trans.set_content_type(ContentType("application/xml", self.encoding))
        print >>self.out, self.model.exportToXml(obj, encoding=self.encoding)


