"""
File name: DuplicatedTransmissionItems.py
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
from WebStack.Generic import ContentType
from libPriyom import *
from API import API, CallSyntax, Argument

class DupeRecord(object):
    def __init__(self, doc, node):
        self.node = node
        self.doc = doc
        self.items = []
        
    def add(self, broadcast, transmission, item):
        if transmission.ID in self.items:
            return
        self.items.append(transmission.ID)
        
        node = XMLIntf.SubElement(self.node, u"duplicate-entry")
        broadcast.toDom(node)
        transmission.toDom(node)
        
        
        contents = node.find(u"{{{0}}}transmission".format(XMLIntf.namespace)).find(u"{{{0}}}Contents".format(XMLIntf.namespace))
        index = transmission.blocks.index(item)
        
        contents[index].set(u"highlighted", u"true")

class DuplicatedTransmissionItemsAPI(API):
    title = u"getDuplicatedTransmissionItems"
    shortDescription = u"get a list of duplicated transmission items"
    
    docArgs = [
        Argument(u"stationId", u"station id", u"select the station at which to look", metavar="stationid"),
        Argument(u"tableId", u"class table id", u"select the transmission class table to look at", metavar="classtableid"),
        Argument(u"equalFields", u"comma separated list", u"transmission item fields to look at (all if omitted)", metavar="equalfields", optional=True),
        Argument(u"includeOtherStationsWithin", u"integer seconds", u"how many seconds transmissions of other stations with same contents may be away to be selected", metavar="seconds", optional=True)
    ]
    docCallSyntax = CallSyntax(docArgs, u"?{0}&{1}&{2}&{3}")

    
    def handle(self, trans):
        stationId = self.getQueryInt("stationId", "must be a station id")
        station = self.store.get(Station, stationId)
        if station is None:
            self.parameterError("stationId", "Station does not exist")
        
        tableId = self.getQueryInt("tableId", "must be a class table id")
        table = self.store.get(TransmissionTable, tableId)
        if table is None:
            self.parameterError("tableId", "Table does not exist")
            
        matchFields = [s for s in (item.lstrip().rstrip() for item in self.query.get("equalFields", u"").split(u",")) if len(s) > 0]
        if len(matchFields) == 0:
            matchFields = None
        else:
            for field in matchFields:
                if not hasattr(table, field):
                    self.parameterError("equalFields", "{0} is not a valid field for this table.".format(field))
                
        includeOtherStationsWithin = self.getQueryIntDefault("includeOtherStationsWithin", 86400, "must be integer seconds")
        
        
        lastModified, items = self.priyomInterface.getDuplicateTransmissions(table, station, matchFields, includeOtherStationsWithin, notModifiedCheck=self.autoNotModified, head=self.head)
        trans.set_content_type(ContentType("application/xml", self.encoding))
        trans.set_header_value("Last-Modified", self.model.formatHTTPTimestamp(float(lastModified)))
        if self.head:
            return
        
        doc = self.model.getExportTree("duplicated-transmissions")
        rootNode = doc.getroot()
        
        dupeDict = {}
        
        for bc1, tx1, txItem1, bc2, tx2, txItem2 in items:
            if matchFields is None:
                key = unicode(txItem1)
            else:
                key = u" ".join((getattr(txItem1, field) for field in matchFields))
            if key in dupeDict:
                rec = dupeDict[key]
                rec.add(bc1, tx1, txItem1)
                rec.add(bc2, tx2, txItem2)
                dupeDict[key] = rec
                continue
            
            node = XMLIntf.SubElement(rootNode, u"duplicated-transmission")
            #node.setAttribute("key", key)
            rec = DupeRecord(doc, node)
            rec.add(bc1, tx1, txItem1)
            rec.add(bc2, tx2, txItem2)
            dupeDict[key] = rec
        
        self.model.etreeToFile(self.out, doc, encoding=self.encoding)
