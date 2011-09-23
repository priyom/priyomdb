from storm.locals import *
import XMLIntf
from Foreign import ForeignHelper
from Broadcast import Broadcast
from Station import Station
from PriyomBase import PriyomBase
import types
from TransmissionParser import TransmissionParserNode, TransmissionParserNodeField
    
class TransmissionClassBase(object):
    def __getitem__(self, index):
        return getattr(self, self.fields[index].FieldName)
    
    def __setitem__(self, index, value):
        return setattr(self, self.fields[index].FieldName, value)
        
    def __len__(self):
        return len(self.fields)
        
    def __iter__(self):
        return ((field, getattr(self, field.FieldName)) for field in self.fields)
        
    def initSupplements(self):
        self.supplements = {}
        for field in self.fields:
            self.supplements[field.FieldName] = ForeignHelper(self, field.FieldName)
        
    def __init__(self, store):
        store.add(self)
        self.initSupplements()
        
    def __storm_loaded__(self):
        self.initSupplements()
        
    def toDom(self, parentNode):
        doc = parentNode.ownerDocument
        group = doc.createElementNS(XMLIntf.namespace, "group")
        group.setAttribute("class", self.TransmissionClassTable.XMLGroupClass)
        group.setAttribute("name", self.TransmissionClassTable.TableName)
        
        for (field, value) in self:
            kind = field.Kind
            XMLIntf.appendTextElement(group, "item", value).setAttribute("class", kind)
            supplement = self.supplements[field.FieldName]
            node = supplement.toDom(group, "item")
            if node is not None:
                node.setAttribute("class", kind)
            
        parentNode.appendChild(group)
        
    def fromDom(self, node, context):
        fields = (field for field in self.fields)
        field = None
        for item in filter(lambda x: (x.nodeType == dom.ELEMENT_NODE) and (x.tagName == u"item"), node.childNodes):
            langCode = item.getAttribute("lang")
            if langCode is None:
                field = fields.__next__()
                setattr(self, field.FieldName, XMLIntf.getText(item))
            else:
                supplement = self.supplements[field.FieldName]
                supplement.ForeignText = XMLIntf.getText(item)
                supplement.LangCode = langCode
    
    def deleteForeignSupplements(self):
        for supplement in self.supplements.itervalues():
            store = Store.of(supplement.supplement)
            if store is not None:
                store.remove(supplement.supplement)

def NewTransmissionClass(table):
    cls = types.ClassType(table.TableName.encode("utf-8"), (TransmissionClassBase, ), {})
    cls.__storm_table__ = table.TableName
    cls.ID = Int(primary = True)
    cls.TransmissionID = Int()
    cls.Order = Int()
    cls.fields = []
    cls.TransmissionClassTable = table
    for field in table.Fields:
        cls.fields.append(field)
        setattr(cls, field.FieldName, Unicode())
    return cls

class TransmissionClassTableField(object):
    __storm_table__ = "transmissionClassTableFields"
    ID = Int(primary = True)
    TransmissionClassTableID = Int()
    FieldNumber = Int()
    FieldName = Unicode()
    Kind = Enum(map={
        "number": "number",
        "codeword": "codeword",
        "plaintext": "plaintext",
        "other": "other"
    })
    MaxLength = Int()
    
    def toDom(self, parentNode, flags = None):
        doc = parentNode.ownerDocument
        fieldNode = doc.createElementNS(XMLIntf.namespace, "field")
        XMLIntf.appendTextElements(fieldNode, [
            ("Number", unicode(self.FieldNumber)),
            ("Name", self.FieldName),
            ("Kind", self.Kind),
            ("MaxLength", unicode(self.MaxLength))
        ])
        parentNode.appendChild(fieldNode)

class TransmissionClassTable(object):
    __storm_table__ = "transmissionClassTables"
    ID = Int(primary = True)
    TransmissionClassID = Int()
    TableName = Unicode()
    DisplayName = Unicode()
    XMLGroupClass = Unicode()
    Fields = ReferenceSet(ID, TransmissionClassTableField.TransmissionClassTableID)
    
    def __storm_loaded__(self):
        self.PythonClass = NewTransmissionClass(self)
        
    def toDom(self, parentNode, flags = None):
        doc = parentNode.ownerDocument
        tableNode = doc.createElementNS(XMLIntf.namespace, "table")
        XMLIntf.appendTextElements(tableNode, [
            ("TableName", self.TableName),
            ("DisplayName", self.DisplayName),
            ("XMLGroupClass", self.XMLGroupClass)
        ])
        
        fieldsNode = doc.createElementNS(XMLIntf.namespace, "fields")
        for field in self.Fields:
            field.toDom(fieldsNode, flags)
        tableNode.appendChild(fieldsNode)
        parentNode.appendChild(tableNode)

class TransmissionClass(PriyomBase):
    __storm_table__ = "transmissionClasses"
    ID = Int(primary = True)
    DisplayName = Unicode()
    RootParserNodeID = Int()
    RootParserNode = Reference(RootParserNodeID, TransmissionParserNode)
    Tables = ReferenceSet(ID, TransmissionClassTable.TransmissionClassID)
    
    def __storm_loaded__(self):
        self.tables = [table for table in self.Tables]
        
    def toDom(self, parentNode, flags = None):
        doc = parentNode.ownerDocument
        classNode = doc.createElementNS(XMLIntf.namespace, "transmission-class")
        XMLIntf.appendTextElements(classNode, [
            ("ID", unicode(self.ID)),
            ("DisplayName", self.DisplayName)
        ])
        
        tablesNode = doc.createElementNS(XMLIntf.namespace, "tables")
        for table in self.Tables:
            table.toDom(tablesNode, flags)
        classNode.appendChild(tablesNode)
        parentNode.appendChild(classNode)
        
    def parseNode(self, node, s):
        expr = node.getExpression()
        match = expr.match(s)
        groups = match.groups()
        if node.Table is not None:
            yield (node.Table, dict(((field.FieldName, groups[field.Group]) for field in node.Fields)))
        else:
            for child in node.Children:
                if child.ParentGroup is None:
                    raise Exception("Malformed node: ParentGroup is None at child node #{0}".format(node.ID)
                for item in self.parseNode(child, groups[child.ParentGroup]):
                    yield item
        
    def parsePlainText(self, s):
        if self.RootParserNode is None:
            raise Exception("No parser assigned.")
        node = self.RootParserNode
        expr = node.getExpression() # re.compile(node.RegularExpression)
        match = expr.match(s)
        if match is None:
            return None
        items = list()
        groups = match.groups()
        for child in node.Children:
            if child.ParentGroup is None:
                raise Exception("Malformed node: ParentGroup is None at child node #{0}".format(node.ID)
            items.extend(self.parseNode(child, groups[child.ParentGroup]))
        

class Transmission(PriyomBase, XMLIntf.XMLStorm):
    __storm_table__ = "transmissions"
    ID = Int(primary = True)
    BroadcastID = Int()
    Broadcast = Reference(BroadcastID, Broadcast.ID)
    Callsign = Unicode()
    Timestamp = Int()
    ClassID = Int()
    Class = Reference(ClassID, TransmissionClass.ID)
    RecordingURL = Unicode()
    Remarks = Unicode()
    
    xmlMapping = {
        u"Recording": "RecordingURL",
        u"Remarks": "Remarks",
        u"StationID": "StationID",
        u"BroadcastID": "BroadcastID",
        u"ClassID": "ClassID"
    }
    
    def updateBlocks(self):
        blocks = []
        store = Store.of(self)
        for table in self.Class.tables:
            for block in store.find(table.PythonClass, table.PythonClass.TransmissionID == self.ID):
                blocks.append(block)
        blocks.sort(cmp=lambda x,y: cmp(x.Order, y.Order))
        self.blocks = blocks
    
    def __init__(self):
        super(Transmission, self).__init__()
        self.ForeignCallsign = None
    
    def __storm_invalidated__(self):
        self.updateBlocks()
        
        self.ForeignCallsign = ForeignHelper(self, "Callsign")
    
    def __storm_loaded__(self):
        self.updateBlocks()
        
        self.ForeignCallsign = ForeignHelper(self, "Callsign")
        
    def _loadCallsign(self, node):
        if node.getAttribute("lang") is not None:
            self.ForeignCallsign.supplement.ForeignText = XMLIntf.getText(node)
            self.ForeignCallsign.supplement.LangCode = XMLIntf.getAttribute("lang")
        else:
            self.Callsign = XMLIntf.getText(node)
        
    """
        Note that loading the contents is, in contrast to most other 
        import operations, replacing instead of merging.
    """
    def _loadContents(self, node):
        store = Store.of(self)
        for block in self.blocks:
            store.remove(block)
        
        if self.Class is None:
            print("Invalid class id: %d" % (self.ClassID))
            return False
        
        for group in filter(lambda x: (x.nodeType == dom.Node.ELEMENT_NODE) and (x.tagName == u"group"), node.childNodes):
            table = store.find(TransmissionClassTable, TransmissionClassTable.TableName == group.getAttribute(u"name"))
            if table is None:
                print("Invalid transmission class table: %s" % (group.getAttribute(u"name")))
                return False
            block = table.PythonClass(store)
            block.fromDom(group)
        
    def _metadataToDom(self, doc, parentNode):
        XMLIntf.appendTextElements(parentNode,
            [
                ("BroadcastID", unicode(self.Broadcast.ID)),
                ("ClassID", unicode(self.Class.ID)),
                ("Callsign", unicode(self.Callsign))
            ]
        )
        self.ForeignCallsign.toDom(parentNode, "Callsign")
        XMLIntf.appendDateElement(parentNode, "Timestamp", self.Timestamp)
        XMLIntf.appendTextElements(parentNode,
            [
                ("Recording", self.RecordingURL),
                ("Remarks", self.Remarks)
            ]
        )
        
    
    def toDom(self, parentNode, flags=None):
        doc = parentNode.ownerDocument
        transmission = doc.createElementNS(XMLIntf.namespace, "transmission")
        XMLIntf.appendTextElement(transmission, "ID", unicode(self.ID))
        self._metadataToDom(doc, transmission)
        
        contents = doc.createElementNS(XMLIntf.namespace, "Contents")
        for block in self.blocks:
            block.toDom(contents)
        transmission.appendChild(contents)
        
        parentNode.appendChild(transmission)
        
    def loadDomElement(self, node, context):
        try:
            {
                u"Callsign": self._loadCallsign,
                u"Contents": self._loadContents
            }[node.tagName](node)
        except KeyError:
            pass


TransmissionParserNode.Table = Reference(TransmissionParserNode.TableID, TransmissionClassTable.ID)
