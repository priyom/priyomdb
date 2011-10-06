"""
File name: Continue.py
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
from WebStack.Generic import EndOfResponse, ContentType
from Selector import Selector

class ContinueSelector(Selector):
    def __init__(self, resource):
        self.resource = resource
        
    def respond(self, trans):
        super(ContinueSelector, self).respond(trans)
        if not "100-continue" in self.getHeaderValuesSplitted("Expect"):
            return self.resource.respond(trans)
        else:
            #trans.rollback()
            #trans.set_response_code(417)
            #trans.set_content_type(ContentType("text/plain", "ascii"))
            # print >>self.out, u"We do not support 100-continue (its a WebStack issue afaik).".encode("ascii")
            trans.set_response_code(417)
            trans.set_content_type(ContentType("text/plain", "ascii"))
            print >>self.out, u"We do not support 100-continue (its a WebStack issue afaik).".encode("ascii")
            raise EndOfResponse
        
