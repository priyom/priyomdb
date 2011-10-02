"""
File name: XMLIntf.py
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
import xml.etree.ElementTree as ElementTree
import datetime
import Formatting
from Helpers import TimeUtils

namespace = u"http://api.priyom.org/priyomdb"
importNamespace = u"http://api.priyom.org/priyomdb/import"
ElementTree.register_namespace(u"priyom", namespace)
ElementTree.register_namespace(u"priyom-import", importNamespace)
debugXml = False

class NoneHandlers:
    @staticmethod
    def asTag(name):
        return ""
        
class XMLStorm(object):
    def loadProperty(self, tagName, data, element, context):
        if debugXml:
            context.log("Failed to map property: %s" % (tagName))
            # print()
        self.loadDomElement(element, context)
        
    def loadDomElement(self, element, context):
        pass
    
    def loadProperties(self, node, context):
        for child in node.childNodes:
            if child.nodeType == dom.Node.ELEMENT_NODE:
                if len(child.childNodes) == 1 and child.childNodes[0].nodeType == dom.Node.TEXT_NODE:
                    if child.tagName in self.xmlMapping:
                        mapped = self.xmlMapping[child.tagName]
                        if type(mapped) == tuple:
                            setattr(self, mapped[0], mapped[1](child.childNodes[0].data))
                        else:
                            setattr(self, mapped, child.childNodes[0].data)
                    else:
                        self.loadProperty(child.tagName, child.childNodes[0].data, child, context)
                elif len(child.childNodes) == 0:
                    if child.tagName in self.xmlMapping:
                        setattr(self, self.xmlMapping[child.tagName], u"")
                    else:
                        self.loadDomElement(child, context)
                else:
                    self.loadDomElement(child, context)
                    
    def fromDom(self, node, context):
        self.loadProperties(node, context)
        
def SubElement(parent, nsLessTagName, attrib={}, xmlns=namespace, **extra):
    return ElementTree.SubElement(parent, u"{{{0}}}{1}".format(xmlns, nsLessTagName), attrib=attrib, **extra)

def appendTextElement(parentNode, name, value, useNamespace=namespace, attrib={}, **extra):
    node = None
    if useNamespace is not None:
        node = SubElement(parentNode, name, xmlns=useNamespace, attrib=attrib, **extra)
    else:
        node = ElementTree.SubElement(parentNode, name, attrib=attrib, **extra)
    node.text = value
    return node

def appendTextElements(parentNode, data, xmlns=namespace, attrib={}, noneHandler=None, **extra):
    builder = ElementTree.SubElement
    if xmlns is not None:
        builder = lambda parent, tag, attrib, **extra: SubElement(parent, tag, attrib=attrib, xmlns=xmlns, **extra)
    for (name, value) in data:
        if value is None:
            if noneHandler is not None:
                value = noneHandler(name)
                if value is None:
                    continue
            else:
                continue
        builder(parentNode, name, attrib, **extra).text = unicode(value)

def appendDateElement(parentNode, name, value, useNamespace = namespace):
    date = TimeUtils.fromTimestamp(value)
    node = appendTextElement(parentNode, name, date.strftime(Formatting.priyomdate), useNamespace = useNamespace)
    node.set(u"unix", unicode(value))
    return node
