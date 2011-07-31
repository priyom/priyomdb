from storm.locals import *
from storm.exceptions import NoStoreError
import XMLIntf

class ForeignSupplement(object):
    __storm_table__ = "foreignSupplement"
    ID = Int(primary=True)
    LocalID = Int()
    FieldName = Unicode()
    ForeignText = Unicode()
    LangCode = Unicode()
    
class ForeignHelper:
    def __init__(self, instance, fieldName):
        self.instance = instance
        self.fieldName = unicode(instance.__storm_table__) + u"." + fieldName
        self.store = Store.of(instance)
        if self.store is None:
            raise NoStoreError("Store is needed to initialize a ForeignHelper")
        self.supplement = self.store.find(ForeignSupplement, 
            (ForeignSupplement.LocalID == self.instance.ID) and
            (ForeignSupplement.FieldName == self.fieldName)).any()
        if self.supplement is None:
            self.supplement = ForeignSupplement()
            self.supplement.LocalID = self.instance.ID
            self.supplement.FieldName = self.fieldName
            self.store.add(self.supplement)
        
    def hasForeign(self):
        return (self.supplement.ForeignText is not None) and (self.supplement.ForeignText != "")
        
    def toDom(self, parentNode, name):
        if self.hasForeign():
            doc = parentNode.ownerDocument
            node = doc.createElementNS(XMLIntf.namespace, name)
            node.appendChild(doc.createTextNode(self.supplement.ForeignText))
            node.setAttribute("lang", self.supplement.LangCode)
            parentNode.appendChild(node)
            return node
        else:
            return None
