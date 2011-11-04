"""
File name: Import.py
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

class ImportAPI(API):
    title = u"import"
    shortDescription = u"Import a priyom transaction xml into the database"
    
    docArgs = []
    docCallSyntax = u""
    docRemarks = u"Must be called in POST mode, the transaction must be sent as request body with Content-Type set to application/xml."
    docRequiredPrivilegues = u"transaction"
    
    def __init__(self, model):
        super(ImportAPI, self).__init__(model)
        self.allowedMethods = frozenset(["GET", "POST"])
    
    def handle(self, trans):
        if trans.get_request_method() == "GET":
            trans.set_response_code(405)
            trans.set_header_value("Allow", "POST")
            trans.set_content_type(ContentType("text/plain"))
            print >>self.out, "POST your transaction data either as application/xml or as application/json according to priyom.org transaction specification"
            return
        trans.set_content_type(ContentType("text/plain", self.encoding))
        
        contentType = str(trans.get_content_type()).split(' ', 1)[0].split(';', 1)[0]
        try:
            method = {
                "application/xml": self.model.importFromXmlStr,
                "application/json": self.model.importFromJsonStr
            }[contentType]
        except KeyError:
            trans.set_response_code(415)
            raise EndOfResponse
        data = trans.get_request_stream().read()
        context = method(data)
        print >>self.out, context.log.get()
