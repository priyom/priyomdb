"""
File name: TransmissionParser.py
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
from storm.locals import *
import re

class NodeError(Exception):
    pass

class TransmissionParserNode(object):
    __storm_table__ = "transmissionParserNode"
    
    ID = Int(primary=True)
    ParentID = Int()
    ParentGroup = Int()
    RegularExpression = Unicode()
    TableID = Int()
    
    def __init__(self):
        self.expression = None
        
    def __storm_loaded__(self):
        self.expression = None
    
    def __storm_invalidated__(self):
        self.expression = None
        
    def getExpression(self):
        if self.expression is None:
            self.expression = re.compile(self.RegularExpression)
        return self.expression
    
TransmissionParserNode.Parent = Reference(TransmissionParserNode.ParentID, TransmissionParserNode.ID)
TransmissionParserNode.Children = ReferenceSet(TransmissionParserNode.ID, TransmissionParserNode.ParentID)
    
class TransmissionParserNodeField(object):
    __storm_table__ = "transmissionParserNodeField"
    
    ID = Int(primary=True)
    ParserNodeID = Int()
    ParserNode = Reference(ParserNodeID, TransmissionParserNode.ID)
    Group = Int()
    ForeignGroup = Int()
    ForeignLangGroup = Int()
    FieldName = Unicode()

TransmissionParserNode.Fields = ReferenceSet(TransmissionParserNode.ID, TransmissionParserNodeField.ParserNodeID)
