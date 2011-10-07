import itertools

__all__ = ['Serializer']

class Serializer(object):
    persistentNamespaceMap = {}
    
    def __init__(self):
        self.namespaceMap = None
        self.encoding = None
        
    def registerNamespacePrefix(self, prefix, uri):
        if len(prefix) > 0 and prefix[0] == u":":
            prefix = prefix[1:]
        if len(prefix) > 0 and prefix[-1] == u":":
            prefix = prefix[:-1]
        if len(prefix) == 0:
            raise ValueError("Empty prefix must not be registered. Use defaultNamespace prefix keyword argument instead.")
        
        for key, value in self.persistentNamespaceMap.iteritems():
            if value == prefix:
                del self.persistentNamespaceMap[key]
                break
        self.persistentNamespaceMap[uri] = prefix
        
    def unregisterNamespacePrefix(self, uri):
        if uri in self.persistentNamespaceMap:
            del self.persistentNamespaceMap[uri]
        
    def encode(self, ustr):
        if type(ustr) == str:
            return ustr
        if type(ustr) == unicode:
            return ustr.encode(self.encoding)
        else:
            return unicode(ustr).encode(self.encoding)
            
    def decode(self, s):
        return s.decode(self.encoding)
            
    def encodeXml(self, ustr):
        if type(ustr) == str:
            return ustr
        if type(ustr) == unicode:
            return ustr.encode(self.encoding, "xmlcharrefreplace")
        else:
            return unicode(ustr).encode(self.encoding, "xmlcharrefreplace")
    
    def escapeAttrib(self, s):
        if u"&" in s:
            s = s.replace(u"&", u"&amp;")
        if u">" in s:
            s = s.replace(u">", u"&gt;")
        if u"<" in s:
            s = s.replace(u"<", u"&lt;")
        if u"\"" in s:
            s = s.replace(u"\"", u"&quot;")
        if u"\n" in s:
            s = s.replace(u"\n", u"&#10;")
        return s
    
    def encodeAttrib(self, s):
        if type(s) == str:
            return s
        if type(s) != unicode:
            s = unicode(s)
        return self.escapeAttrib(s).encode(self.encoding, "xmlcharrefreplace")
        
    def escapeCData(self, s):
        if u"&" in s:
            s = s.replace(u"&", u"&amp;")
        if u">" in s:
            s = s.replace(u">", u"&gt;")
        if u"<" in s:
            s = s.replace(u"<", u"&lt;")
        return s
        
    def encodeCData(self, s):
        if type(s) == str:
            return s
        if type(s) != unicode:
            s = unicode(s)
        return self.escapeCData(s).encode(self.encoding, "xmlcharrefreplace")
    
    def _raiseNonNamespacedAndDefaultNamespaceError(self):
        raise ValueError(u"Cannot serialize XML with default namespace and non qualified tags.")
        
    def _allocateTmpNamespace(self, uri):
        if uri in self.persistentNamespaceMap:
            prefix = self.persistentNamespaceMap[uri]
            self.namespaceMap[uri] = prefix
        else:
            prefix = ":ns{0}".format(self.namespaceCounter)
            self.namespaceMap[uri] = prefix
            self.namespaceCounter += 1
        return prefix
    
    def _parseTreeNamespaces(self, element):
        tag = element.tag.partition("}")
        if len(tag[1]) != 0:
            namespace = tag[0][1:]
            if not namespace in self.namespaceMap:
                self._allocateTmpNamespace(namespace)
        else:
            self.nonNamespaced = True
            
        for child in element:
            self._parseTreeNamespaces(child)
        
    def _serializeElement(self, write, element, isRoot=False):
        tag = element.tag.partition("}")
        namespace = None
        if len(tag[1]) != 0:
            namespace = self.encode(tag[0][1:])
            tag = self.encode(tag[2])
        else:
            tag = tag[0]
        
        if namespace is None and self.defaultNamespace is not None:
            self._raiseNonNamespacedAndDefaultNamespaceError()
        
        qname = tag
        
        if isRoot:
            namespaceAttribs = dict(
                ((prefix, uri) for uri, prefix in self.namespaceMap.iteritems())
            )
        else:
            namespaceAttribs = {}    
        
        tmpPrefix = False
        if namespace is not None:
            if not namespace in self.namespaceMap:
                prefix = self._allocateTmpNamespace(namespace)
                namespaceAttribs[prefix] = namespace
                tmpPrefix = True
            else:
                prefix = self.namespaceMap[namespace]
            qname = "{0}{2}{1}".format(prefix, tag, ":" if len(prefix) > 0 else "")
        
        attribs = " ".join(itertools.chain(
            ('xmlns{2}{0}="{1}"'.format(key, self.encodeAttrib(self.decode(value)), ":" if len(key) > 0 else "") for key, value in sorted(namespaceAttribs.iteritems(), key=lambda x: x[0])),
            ('{0}="{1}"'.format(key, self.encodeAttrib(value)) for key, value in element.items())
        ))
        
        write("<{0}{1}{2}".format(
            qname,
            " " if len(attribs) > 0 else "",
            attribs
        ))
        del attribs
        del namespaceAttribs
        
        text = element.text
        if text or len(element):
            write(">")
            if text:
                write(self.encodeCData(self.encode(text)))
            for child in element:
                self._serializeElement(write, child)
            write("</{0}>".format(qname))
        else:
            write(" />")
        
        if tmpPrefix:
            del self.namespaceMap[namespace]
        
        if element.tail:
            write(self.encodeCData(element.tail))
        
    def serializeTree(self, file, tree, encoding="UTF-8", xmlHeader=True, defaultNamespace=None, headerNamespaces=False):
        self.encoding = encoding
        self.namespaceMap = {}
        #self.namespaceMap = dict(
        #    ((self.encode(key), self.encode(value)) for key, value in self.persistentNamespaceMap.iteritems())
        #)
        if defaultNamespace is not None:
            self.namespaceMap[self.encode(defaultNamespace)] = ""
        
        self.namespaceCounter = 0
        self.defaultNamespace = defaultNamespace
        if headerNamespaces:
            self.nonNamespaced = False
            self._parseTreeNamespaces(tree.getroot())
            if self.nonNamespaced and defaultNamespace:
                self._raiseNonNamespacedAndDefaultNamespaceError()
        
        if xmlHeader:
            file.write("""<?xml version="1.0" encoding="{0}"?>\n""".format(encoding))
        
        self._serializeElement(file.write, tree.getroot(), isRoot=True)
        
        self.encoding = None
    
