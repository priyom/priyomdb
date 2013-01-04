"""
File name: Transmission.py
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
from storm.locals import *
import XMLIntf
import types
import itertools
from libPriyom.PriyomBase import PriyomBase
from libPriyom.Foreign import ForeignHelper
from libPriyom.Broadcast import Broadcast
from libPriyom.Station import Station
from libPriyom.TransmissionParser import TransmissionParserNode, TransmissionParserNodeField, NodeError

class Transmission(PriyomBase, XMLIntf.XMLStorm):
    __storm_table__ = "transmissions"
    ID = Int(primary = True)
    BroadcastID = Int()
    Broadcast = Reference(BroadcastID, Broadcast.ID)
    Callsign = Unicode()
    Timestamp = Int()
    ClassID = Int()
    RecordingURL = Unicode()
    Remarks = Unicode()

    xmlMapping = {
        u"Recording": "RecordingURL",
        u"Remarks": "Remarks"
    }

    def updateBlocks(self):
        blocks = []
        store = Store.of(self)
        for table in self.Class.tables:
            for block in store.find(table.PythonClass, table.PythonClass.TransmissionID == self.ID):
                blocks.append(block)
        blocks.sort(cmp=lambda x,y: cmp(x.Order, y.Order))
        self._blocks = blocks

    def __init__(self):
        super(Transmission, self).__init__()
        self.ForeignCallsign = None
        self._blocks = None
        self._blockUpdate = None

    def __storm_invalidated__(self):
        self.ForeignCallsign = ForeignHelper(self, "Callsign")

    def __storm_loaded__(self):
        self.ForeignCallsign = ForeignHelper(self, "Callsign")

    def _loadCallsign(self, element, context):
        if self.ForeignCallsign is None:
            self.ForeignCallsign = ForeignHelper(self, "Callsign")

        lang = element.get(u"lang")
        if lang is not None:
            self.ForeignCallsign.Value = unicode(element.text)
            self.ForeignCallsign.LangCode = unicode(lang)
        else:
            self.Callsign = unicode(element.text)

    def _loadBroadcastID(self, element, context):
        self.Broadcast = context.resolveId(Broadcast, int(element.text))

    def _loadClassID(self, element, context):
        self.Class = context.resolveId(TransmissionClass, int(element.text))

    """
        Note that loading the contents is, in contrast to most other
        import operations, replacing instead of merging.
    """
    def _loadContents(self, node, context):
        store = Store.of(self)
        for block in self.blocks:
            store.remove(block)

        if self.Class is None:
            print("Invalid class id: %d" % (self.ClassID))
            return False

        for group in node.iterfind("{{{0}}}group".format(XMLIntf.importNamespace)):
            table = store.find(TransmissionTable, TransmissionTable.TableName == group.getAttribute(u"name")).any()
            if table is None:
                print("Invalid transmission class table: %s" % (group.get(u"name")))
                return False
            block = table.PythonClass(store)
            block.fromDom(group, context)

    def _metadataToDom(self, parentNode):
        XMLIntf.appendTextElements(parentNode,
            (
                (u"BroadcastID", self.Broadcast.ID),
                (u"ClassID", self.Class.ID),
                (u"Callsign", self.Callsign)
            )
        )
        self.ForeignCallsign.toDom(parentNode, u"Callsign")
        XMLIntf.appendDateElement(parentNode, u"Timestamp", self.Timestamp)
        XMLIntf.appendTextElements(parentNode,
            (
                (u"Recording", self.RecordingURL),
                (u"Remarks", self.Remarks)
            )
        )


    def toDom(self, parentNode, flags=None):
        transmission = XMLIntf.SubElement(parentNode, u"transmission")
        XMLIntf.SubElement(transmission, u"ID").text = unicode(self.ID)
        self._metadataToDom(transmission)

        contents = XMLIntf.SubElement(transmission, u"Contents")
        for block in self.blocks:
            block.toDom(contents)

    def loadElement(self, tag, element, context):
        try:
            {
                u"BroadcastID": self._loadBroadcastID,
                u"ClassID": self._loadClassID,
                u"Callsign": self._loadCallsign,
                u"Contents": self._loadContents
            }[tag](element, context)
        except KeyError:
            pass

    def clear(self):
        store = Store.of(self)
        for table in list(self.Class.tables):
            for block in list(store.find(table.PythonClass, table.PythonClass.TransmissionID == self.ID)):
                block.deleteForeignSupplements()
                store.remove(block)

    def setParsedContents(self, contents):
        self.clear()
        store = Store.of(self)
        for order, rowData in enumerate(contents):
            tableClass = rowData[0].PythonClass
            contentDict = rowData[1]

            row = tableClass(store)
            try:
                row.Transmission = self
                row.Order = order

                for key, (value, foreign) in contentDict.iteritems():
                    setattr(row, key, value)
                    if foreign is not None:
                        supplement = row.supplements[key]
                        try:
                            supplement.LangCode = foreign[0]
                            supplement.Value = foreign[1]
                        except:
                            supplement.removeSupplement()
            except:
                store.remove(row)

    @property
    def Contents(self):
        return u" ".join((unicode(block) for block in self.blocks))

    @Contents.setter
    def Contents(self, value):
        try:
            parsed = self.Class.parsePlainText(value)
        except NodeError as e:
            raise ValueError(unicode(e))
        self.setParsedContents(parsed)
        self.touch()

    @Contents.deleter
    def Contents(self):
        self.clear()

    def __unicode__(self):
        return u"Transmission with callsign {0} and {1} segments".format(self.Callsign, len(self.blocks))

    @property
    def blocks(self):
        if not hasattr(self, "_blocks") or not hasattr(self, "_blockUpdate"):
            self._blocks = None
            self._blockUpdate = None
        self.Modified = AutoReload
        if self._blockUpdate is None or self._blockUpdate != self.Modified:
            self.updateBlocks()
        return self._blocks

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
        group = XMLIntf.SubElement(parentNode, u"group", {
            u"class": self.TransmissionTable.XMLGroupClass,
            u"name": self.TransmissionTable.TableName
        })

        for (field, value) in self:
            kind = field.Kind
            XMLIntf.SubElement(group, u"item", {
                u"class": kind
            }).text = value
            supplement = self.supplements[field.FieldName]
            node = supplement.toDom(group, u"item", {
                u"class": kind
            })

    def fromDom(self, element, context):
        fields = iter((field for field in self.fields))
        field = None
        prevHadLangCode = False
        for item in element.iterfind(u"{{{0}}}item".format(XMLIntf.importNamespace)):
            langCode = item.get(u"lang")
            if langCode is None or len(langCode) == 0:
                if not prevHadLangCode and field is not None:
                    del self.supplements[field.FieldName].Value
                field = next(fields)
                setattr(self, field.FieldName, unicode(item.text))
            else:
                supplement = self.supplements[field.FieldName]
                supplement.Value = unicode(item.text)
                supplement.LangCode = unicode(langCode)

    def deleteForeignSupplements(self):
        for supplement in self.supplements.itervalues():
            supplement.removeSupplement()

    def formatField(self, fieldName):
        value = getattr(self, fieldName)
        supplement = self.supplements[fieldName]
        if supplement.hasForeign():
            return u"{0}/{1}:{2}".format(value, supplement.Value, supplement.LangCode)
        else:
            return u"{0}".format(value)

    def __unicode__(self):
        return u" ".join((self.formatField(field.FieldName) for field in self.fields))

def NewTransmissionClass(table):
    cls = types.ClassType(table.TableName.encode("utf-8"), (TransmissionClassBase, ), {})
    cls.__storm_table__ = table.TableName
    cls.ID = Int(primary = True)
    cls.TransmissionID = Int()
    cls.Transmission = Reference(cls.TransmissionID, Transmission.ID)
    cls.Order = Int()
    cls.fields = []
    cls.TransmissionTable = table
    for field in table.Fields:
        cls.fields.append(field)
        setattr(cls, field.FieldName, Unicode())
    return cls

class TransmissionTableField(object):
    __storm_table__ = "transmissionTableFields"
    ID = Int(primary = True)
    TransmissionTableID = Int()
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
        fieldNode = XMLIntf.SubElement(parentNode, u"field")
        XMLIntf.appendTextElements(fieldNode, (
            (u"Number", unicode(self.FieldNumber)),
            (u"Name", self.FieldName),
            (u"Kind", self.Kind),
            (u"MaxLength", unicode(self.MaxLength))
        ))

class TransmissionTable(object):
    __storm_table__ = "transmissionTables"
    ID = Int(primary = True)
    TableName = Unicode()
    DisplayName = Unicode()
    XMLGroupClass = Unicode()
    Fields = ReferenceSet(ID, TransmissionTableField.TransmissionTableID)

    def __storm_loaded__(self):
        self.PythonClass = NewTransmissionClass(self)

    def toDom(self, parentNode, flags = None):
        tableNode = XMLIntf.SubElement(parentNode, u"table")
        XMLIntf.appendTextElements(tableNode, (
            ("TableName", self.TableName),
            ("DisplayName", self.DisplayName),
            ("XMLGroupClass", self.XMLGroupClass)
        ))

        fieldsNode = XMLIntf.SubElement(tableNode, u"fields")
        for field in self.Fields:
            field.toDom(fieldsNode, flags)

class TransmissionClass(PriyomBase):
    __storm_table__ = "transmissionClasses"
    ID = Int(primary = True)
    DisplayName = Unicode()
    RootParserNodeID = Int()
    RootParserNode = Reference(RootParserNodeID, TransmissionParserNode.ID)

    def __storm_loaded__(self):
        self.tables = [table for table in self.Tables]

    def toDom(self, parentNode, flags = None):
        classNode = XMLIntf.SubElement(parentNode, u"transmission-class")
        XMLIntf.appendTextElements(classNode, (
            (u"ID", unicode(self.ID)),
            (u"DisplayName", self.DisplayName)
        ))

        tablesNode = XMLIntf.SubElement(classNode, u"tables")
        for table in self.Tables:
            table.toDom(tablesNode, flags)

    def parseNode(self, node, s):
        expr = node.getExpression()
        if node.Table is not None:
            for match in expr.finditer(s):
                d = {}
                for field in node.Fields:
                    contents = match.group(field.Group+1)
                    if field.ForeignGroup is not None and field.ForeignLangGroup is not None:
                        foreignLangCode = match.group(field.ForeignLangGroup+1)
                        foreignContents = match.group(field.ForeignGroup+1)
                        if (not foreignContents) ^ (not foreignLangCode):
                            raise ValueError("Foreign contents or lang code given without the respective other")
                        foreignInfo = (foreignLangCode, foreignContents)
                    else:
                        foreignInfo = None

                    d[field.FieldName] = (contents, foreignInfo)
                yield (node.Table, d)
        else:
            match = expr.match(s)
            if match is None:
                raise ValueError("Sub-match failed")
            groups = match.groups()
            for child in node.Children:
                if child.ParentGroup is None:
                    raise NodeError("Malformed node: ParentGroup is None at child node #{0}".format(node.ID))
                for item in self.parseNode(child, groups[child.ParentGroup]):
                    yield item

    def parsePlainText(self, s):
        if self.RootParserNode is None:
            raise NodeError("No parser assigned.")
        node = self.RootParserNode
        expr = node.getExpression() # re.compile(node.RegularExpression)
        print(expr.pattern)
        match = expr.match(s)
        if match is None:
            raise ValueError("Root match failed")
        items = list()
        groups = match.groups()

        for child in Store.of(node).find(TransmissionParserNode, TransmissionParserNode.ParentID == node.ID).order_by(Asc(TransmissionParserNode.ParentGroup)):
            if child.ParentGroup is None:
                raise NodeError("Malformed node: ParentGroup is None at child node #{0}".format(node.ID))
            items.extend(self.parseNode(child, groups[child.ParentGroup]))
        return items

    def __unicode__(self):
        return self.DisplayName

class TransmissionClassTable(object):
    __storm_table__ = "transmissionClassTables"
    __storm_primary__ = "ClassID", "TableID"
    ClassID = Int()
    TableID = Int()

TransmissionClass.Tables = ReferenceSet(
    TransmissionClass.ID,
    TransmissionClassTable.ClassID,
    TransmissionClassTable.TableID,
    TransmissionTable.ID
)

Transmission.Class = Reference(Transmission.ClassID, TransmissionClass.ID)
TransmissionParserNode.Table = Reference(TransmissionParserNode.TableID, TransmissionTable.ID)
