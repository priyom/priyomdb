"""
File name: HTMLIntf.py
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
import libPriyom.XMLIntf as XMLIntf
import ElementTreeHelper.Serializer

xhtmlNamespace = XMLIntf.xhtmlNamespace

_serializer = ElementTreeHelper.Serializer.Serializer(useNamespaces=True)
_serializer.registerNamespacePrefix(u"priyom", XMLIntf.namespace)
_serializer.registerNamespacePrefix(u"priyom-import", XMLIntf.importNamespace)
_serializer.registerNamespacePrefix(u"xhtml", xhtmlNamespace)

def Serializer():
    global _serializer
    return _serializer

def Element(nsLessTagName, attrib={}, xmlns=XMLIntf.xhtmlNamespace, **extra):
    return ElementTree.Element(u"{{{0}}}{1}".format(xmlns, nsLessTagName), attrib=attrib, **extra)

def SubElement(parent, nsLessTagName, attrib={}, xmlns=XMLIntf.xhtmlNamespace, **extra):
    return XMLIntf.SubElement(parent, nsLessTagName, attrib=attrib, xmlns=xmlns, **extra)
