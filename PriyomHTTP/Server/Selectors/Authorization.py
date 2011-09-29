"""
File name: Authorization.py
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
from WebStack.Generic import EndOfResponse

class AuthorizationSelector(object):
    def __init__(self, resource, requiredCap):
        self.resource = resource
        self.requiredCap = requiredCap
        if type(self.requiredCap) != list:
            self.requiredCap = [self.requiredCap]
        
        self.title = self.resource.title
        if hasattr(self.resource, "shortDescription"):
            self.shortDescription = self.resource.shortDescription
        
    def respond(self, trans):
        for cap in self.requiredCap:
            if cap in trans.apiCaps:
                return self.resource.respond(trans)
        self.authFailed(trans)
        
    def doc(self, trans, breadcrumbs):
        # transparently pass this through
        return self.resource.doc(trans, breadcrumbs)
        
    def authFailed(self, trans):
        trans.set_response_code(401)
        if not trans.apiAuth:
            if trans.apiAuthError is not None:
                print >>trans.get_response_stream(), trans.apiAuthError
            else:
                print >>trans.get_response_stream(), "Not authenticated."
        else:
            print >>trans.get_response_stream(), "Missing capabilities."
        raise EndOfResponse
