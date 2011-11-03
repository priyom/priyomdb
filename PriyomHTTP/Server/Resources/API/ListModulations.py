"""
File name: ListModulations.py
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

class ListModulationsAPI(API):
    title = u"listModulations"
    shortDescription = u"return a list of modulations known to the database"
    
    docArgs = []
    docCallSyntax = CallSyntax(docArgs, u"")
    
    
    def handle(self, trans):
        lastModified = self.model.getLastUpdate()
        trans.set_content_type(ContentType("application/xml", self.encoding))
        trans.set_header_value("Last-Modified", self.model.formatHTTPTimestamp(float(lastModified)))
        if self.head:
            return 
        self.autoNotModified(lastModified)
        
        items = self.store.find(Modulation)
        self.model.limitResults(items)
        
        doc = self.model.getExportTree("priyom-modulations")
        rootNode = doc.getroot()
        for modulation in items:
            modulation.toDom(rootNode)
        self.model.etreeToFile(self.out, doc, encoding=self.encoding)

