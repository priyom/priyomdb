# encoding=utf-8
"""
File name: Editor.py
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
from WebStack.Generic import ContentType, EndOfResponse
import EditRegistry
from ..HTMLResource import HTMLResource
from .. import HTMLIntf

class EditorResource(HTMLResource):
    def __init__(self, model):
        super(EditorResource, self).__init__(model)
        
    def notFound(self):
        #self.trans.rollback()
        self.trans.set_response_code(404)
        #self.trans.set_content_type(ContentType("text/plain", self.encoding))
        #print >>self.out, )
        #raise EndOfResponse
        HTMLIntf.SubElement(self.body, u"p").text = u"Resource not found: \"{0}{1}\"".format(self.trans.get_processed_virtual_path_info(), self.trans.get_virtual_path_info())
        
    def redirect(self):
        self.trans.rollback()
        path_without_query = self.trans.get_path_without_query("utf-8")
        query_string = self.trans.get_query_string()
        if query_string:
            query_string = "?" + query_string
        self.trans.redirect(self.trans.encode_path(path_without_query, "utf-8") + "/" + query_string)
        raise EndOfResponse
        
    def _(self, trans, path):
        pass
        
    def _tables(self, trans, path):
        if len(path) == 0:
            self.redirect()
        if len(path) > 1:
            self.notFound()
        table = path[0]
        if not table:
            table = None
        
        
        
    def buildDoc(self, trans, elements):
        path = trans.get_virtual_path_info().split('/')[1:]
        if len(path) == 0:
            self.redirect()
        try:
            method = {
                u"": self._,
                u"tables": self._tables
            }[path[0]]
        except KeyError:
            self.notFound()
        else:
            method(trans, path[1:])
