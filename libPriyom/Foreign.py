"""
File name: Foreign.py
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
            And((ForeignSupplement.LocalID == self.instance.ID),
            (ForeignSupplement.FieldName == self.fieldName))).any()
            
    def generateSupplement(self):
        self.supplement = ForeignSupplement()
        self.supplement.FieldName = self.fieldName
        self.supplement.LocalID = self.instance.ID
        self.store.add(self.supplement)
    
    @property
    def Value(self):
        if self.supplement is None:
            return None
        else:
            return self.supplement.ForeignText
            
    @Value.setter
    def Value(self, value):
        if self.supplement is None:
            self.generateSupplement()
        self.supplement.ForeignText = value
        
    @Value.deleter
    def Value(self):
        self.store.remove(self.supplement)
        self.supplement = None
        
    @property
    def LangCode(self):
        if self.supplement is None:
            return None
        else:
            return self.supplement.LangCode
            
    @LangCode.setter
    def LangCode(self, value):
        if self.supplement is None:
            self.generateSupplement()
        self.supplement.LangCode = value
    
    @LangCode.deleter
    def LangCode(self):
        self.store.remove(self.supplement)
        self.supplement = None
        
    def hasForeign(self):
        return self.supplement is not None and bool(self.supplement)
        
    def toDom(self, parentNode, name, attrib={}):
        if self.hasForeign():
            node = XMLIntf.SubElement(parentNode, name, attrib=attrib, lang=self.supplement.LangCode)
            node.text = self.supplement.ForeignText
            return node
        else:
            return None
