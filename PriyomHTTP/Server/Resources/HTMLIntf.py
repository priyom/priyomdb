import xml.etree.ElementTree as ElementTree
from libPriyom import XMLIntf

xhtmlNamespace = XMLIntf.xhtmlNamespace

def Element(nsLessTagName, attrib={}, xmlns=XMLIntf.xhtmlNamespace, **extra):
    return ElementTree.Element(u"{{{0}}}{1}".format(xmlns, nsLessTagName), attrib=attrib, **extra)

def SubElement(parent, nsLessTagName, attrib={}, xmlns=XMLIntf.xhtmlNamespace, **extra):
    return XMLIntf.SubElement(parent, nsLessTagName, attrib=attrib, xmlns=xmlns, **extra)
