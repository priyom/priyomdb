"""
File name: Imports.py
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
import XMLIntf
import Log

class ImportContext(object):
    def __init__(self, store):
        self.classes = dict()
        self.store = store
        self.log = Log.Log(["import"], "import")
    
    def _addObject(self, cls, id, obj):
        if not cls in self.classes:
            self.classes[cls] = dict()
        self.classes[cls][id] = obj
        
    def resolveId(self, cls, id):
        if id < 0:
            if not cls in self.classes:
                return None
            if not id in self.classes[cls]:
                return None
            return self.classes[cls][id]
        else:
            return self.store.get(cls, id)
            
    def _getForImport(self, cls, id):
        obj = None
        if id < 0:
            obj = cls()
            self.store.add(obj)
        else:
            obj = self.store.get(cls, id)
            if obj is None:
                self.log(u"%s with id %d was requested, but its not in the database. Import will be skipped." % (unicode(cls), id))
        return obj
    
    def importFromETree(self, element, cls):
        idNode = element.find(u"{{{0}}}ID".format(XMLIntf.importNamespace)
        if idNode is None:
            if node.get(u"id") is not None:
                return self.resolveId(int(node.get(u"id")))
            else:
                self.log("Found id-less node: %s" % (node.tagName))
                return None
        id = int(idNode.text)
        obj = self._getForImport(cls, id)
        if obj is None:
            return obj
        obj.fromDom(element, self)
        if id < 0:
            self._addObject(cls, id, obj) # important: use id here, we want to be able to resolve negative ids later!
        self.store.flush()
        self.log(u"%s %s with id %d (%s). Assigned id: %d" % ("Imported" if id < 0 else "Updated", unicode(cls), id, unicode(obj), obj.ID))
        return obj
        
    def importFromJsonSubtree(self, subtree, cls):
        if type(subtree) == int:
            return self.resovleId(subtree)
        if type(subtree) != dict:
            self.log("Found non-object in json code where object was expected.")
            return None
        id = int(subtree["id"])
        obj = self._getForImport(cls, id)
        if obj is None:
            return obj
        obj.fromJson(subtree, self)
        if id < 0:
            self._addObject(cls, id, obj)
        return obj
        
        

