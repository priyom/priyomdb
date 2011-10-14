# encoding=utf-8
"""
File name: Home.py
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
from ..HTMLResource import HTMLResource
from .. import HTMLIntf

class AdminHomeResource(HTMLResource):
    def __init__(self, model):
        super(AdminHomeResource, self).__init__(model)
    
    def buildDoc(self, trans, elements):
        sec = HTMLIntf.SubElement(self.body, u"section")
        head = HTMLIntf.SubElement(sec, u"header")
        HTMLIntf.SubElement(head, u"h1").text = u"priyom.org/admin"
        HTMLIntf.SubElement(sec, u"p").text = u"Welcome to the administration area of api.priyom.org. Here you can more or less directly modify database contents."
        HTMLIntf.SubElement(sec, u"p").text = u"Choose which section of the admin area you want to use:"
        ul = HTMLIntf.SubElement(sec, u"ul")
        li = HTMLIntf.SubElement(ul, u"li")
        a = HTMLIntf.SubElement(HTMLIntf.SubElement(li, u"p"), u"a", href="tables/")
        a.text = u"Table editor"
        HTMLIntf.SubElement(li, u"p").text = u"This tool allows you to edit database contents in a safe manner (that is, with consistency checks etc.)"
