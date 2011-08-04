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
    
    def importFromDomNode(self, node, cls):
        idNode = XMLIntf.getChild(node, "id")
        if idNode is None:
            if node.hasAttribute("id"):
                return self.resolveId(int(node.getAttribute("id")))
            else:
                self.log("Found id-less node: %s" % (node.tagName))
        id = int(idNode.childNodes[0].data)
        obj = self._getForImport(cls, id)
        if obj is None:
            return obj
        obj.fromDom(node, self)
        if id < 0:
            self._addObject(cls, id, obj) # important: use id here, we want to be able to resolve negative ids later!
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
        
        
