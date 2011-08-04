import xml.dom.minidom as dom
import datetime
import Formatting

namespace = "http://priyom.org/station-db"
debugXml = True

class NoneHandlers:
    @staticmethod
    def asTag(name):
        return ""
        
class XMLStorm(object):
    def loadProperty(self, tagName, data, element):
        if debugXml:
            print("Failed to map property: %s" % (tagName))
        self.loadDomElement(element)
        
    def loadDomElement(self, element):
        pass
    
    def loadProperties(self, node):
        for child in node.childNodes:
            if child.nodeType == dom.Node.ELEMENT_NODE:
                if len(child.childNodes) == 1 and child.childNodes[0].nodeType == dom.Node.TEXT_NODE:
                    if child.tagName in self.xmlMapping:
                        setattr(self, self.xmlMapping[child.tagName], child.childNodes[0].data)
                    else:
                        self.loadProperty(child.tagName, child.childNodes[0].data, child)
                else:
                    self.loadDomElement(child)
                    
    def fromDom(self, node):
        self.loadProperties(node)
    
def buildTextElementNS(doc, name, value, namespace):
    node = doc.createElementNS(namespace, name)
    if len(value) > 0:
        node.appendChild(doc.createTextNode(value))
    return node
    
def buildTextElement(doc, name, value):
    node = doc.createElement(name)
    if len(value) > 0:
        node.appendChild(doc.createTextNode(value))
    return node

def appendTextElement(parentNode, name, value, useNamespace = namespace, doNotAppend = False):
    node = None
    if useNamespace is not None:
        node = buildTextElementNS(parentNode.ownerDocument, name, value, useNamespace)
    else:
        node = buildTextElement(parentNode.ownerDocument, name, value)
    if not doNotAppend:
        parentNode.appendChild(node)
    return node

def appendTextElements(parentNode, data, useNamespace = namespace, noneHandler = None):
    doc = parentNode.ownerDocument
    builder = buildTextElement
    if useNamespace is not None:
        builder = lambda doc, name, value: buildTextElementNS(doc, name, value, useNamespace)
    for (name, value) in data:
        if value is None:
            if noneHandler is not None:
                value = noneHandler(name)
                if value is None:
                    continue
            else:
                continue
        parentNode.appendChild(builder(doc, name, value))

def appendDateElement(parentNode, name, value, useNamespace = namespace, doNotAppend = False):
    date = datetime.datetime.fromtimestamp(value)
    node = appendTextElement(parentNode, name, date.strftime(Formatting.priyomdate), useNamespace, True)
    node.setAttribute("unix", unicode(value))
    if not doNotAppend:
        parentNode.appendChild(node)
    return node
    
def getChild(node, tagName):
    for child in node.childNodes:
        if child.nodeType == dom.Node.ELEMENT_NODE:
            if child.tagName == tagName:
                return child
    return None

def getText(node):
    s = ""
    for child in node.childNodes:
        if child.nodeType == dom.Node.TEXT_NODE:
            s = s + child.data
    return s
