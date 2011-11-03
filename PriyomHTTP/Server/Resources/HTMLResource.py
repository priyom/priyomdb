"""
File name: HTMLResource.py
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
from Resource import Resource, CallSyntax, Argument
from libPriyom import XMLIntf
import xml.etree.ElementTree as ElementTree
from cfg_priyomhttpd import misc, application
from WebStack.Generic import ContentType
import HTMLIntf

class HTMLResource(Resource):
    def __init__(self, model):
        super(HTMLResource, self).__init__(model)
        
    def SubElement(self, parent, nsLessTagName, attrib={}, xmlns=XMLIntf.xhtmlNamespace, **extra):
        return XMLIntf.SubElement(parent, nsLessTagName, attrib, xmlns, **extra)
        
    def link(self, href, rel="stylesheet", type="text/css"):
        return self.SubElement(self.head, u"link", rel=rel, type=type, href=self.model.rootPath(href))
        
    def script(self, href, type="text/javascript"):
        return self.SubElement(self.head, u"script", type=type, src=self.model.rootPath(href))
        
    def br(self, parent, tail=u""):
        br = self.SubElement(parent, u"br")
        br.tail = tail
        return br
    
    def input(self, parent, name=u"", type=u"text", value=u"", attrib=None, **extra):
        if attrib is None:
            attrib = {}
        attrib.update(extra)
        return self.SubElement(parent, u"input", name=name, type=type, value=value, attrib=attrib)
        
    def setTitle(self, title):
        self.title.text = u"{0}{1}{2}".format(
            title,
            (misc.get("titleSeparator", u" ") + application["name"]) if "name" in application else u"",
            (misc.get("titleSeparator", u" ") + application["host"]) if "host" in application else u""
        )
    
    def handle(self, trans):
        trans.set_content_type(ContentType(self.xhtmlContentType, self.encoding))
        
        doc = ElementTree.ElementTree(ElementTree.Element(u"{{{0}}}html".format(XMLIntf.xhtmlNamespace)))
        self.html = doc.getroot()
        
        self.head = self.SubElement(self.html, u"head")
        self.title = self.SubElement(self.head, u"title")
        
        self.body = self.SubElement(self.html, u"body")
        
        self.buildDoc(trans, (self.html, self.head, self.body))
        
        self.model.etreeToFile(self.out, doc, self.encoding, XMLIntf.xhtmlNamespace, serializer=self.model.xhtmlSerializer)
        
    def buildDoc(trans, elements):
        pass
