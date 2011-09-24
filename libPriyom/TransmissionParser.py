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
    FieldName = Unicode()

TransmissionParserNode.Fields = ReferenceSet(TransmissionParserNode.ID, TransmissionParserNodeField.ParserNodeID)
