"""
File name: List.py
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

class ListAPI(API):
    def __init__(self, model, cls, requriedPrivilegue = None):
        super(ListAPI, self).__init__(model)
        self.cls = cls
        self.title = "list{0}".format(cls.__name__)
        self.shortDescription = "return a list of {0} objects".format(cls.__name__)
        self.docArgs = []
        self.docCallSyntax = CallSyntax(self.docArgs, u"")
        if requriedPrivilegue is not None:
            self.docRequiredPrivilegues = requriedPrivilegue
    
    def handle(self, trans):
        lastModified, items = self.priyomInterface.listObjects(self.cls, limiter=self.model, notModifiedCheck=self.autoNotModified, head=self.head)
        trans.set_content_type(ContentType("application/xml", self.encoding))
        trans.set_header_value("Last-Modified", self.model.formatHTTPTimestamp(float(lastModified)))
        if self.head:
            return
        
        # flags must not be enabled here; otherwise a permission leak
        # is possible.
        self.model.exportListToFile(self.out, items, self.cls, flags = frozenset(), encoding=self.encoding)

