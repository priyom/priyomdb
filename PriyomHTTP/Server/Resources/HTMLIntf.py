import xml.etree.ElementTree as ElementTree
from libPriyom import XMLIntf
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
