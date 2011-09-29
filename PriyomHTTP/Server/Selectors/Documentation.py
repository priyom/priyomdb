"""
File name: Documentation.py
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
from cfg_priyomhttpd import application, doc, misc

class DocumentationSelector(object):
    path_encoding = "utf-8"
    
    def __init__(self, resource):
        self.resource = resource
    
    def respond(self, trans):
        if hasattr(self.resource, "doc"):
            trans.encoding = "utf-8"
            breadcrumbs = None
            if doc.get("breadcrumbs", {}).get("enabled", False):
                breadcrumbs = list()
            return self.resource.doc(trans, breadcrumbs)
        else:
            trans.rollback()
            trans.set_response_code(501)
            trans.set_content_type(ContentType("text/plain", "utf-8"))
            print >>trans.get_response_stream(), u"Documentation not implemented.".encode("utf-8")
