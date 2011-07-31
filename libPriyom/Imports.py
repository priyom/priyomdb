from storm.locals import *
import XMLIntf

def importSimple(store, cls, node):
    idNode = XMLIntf.getChild(node, "id")
    if idNode is None:
        return None
    id = int(idNode.childNodes[0].data)
    obj = None
    if id < 0:
        obj = cls()
        store.add(obj)
    else:
        obj = store.get(cls, id)
        if obj is None:
            raise ValueError("Invalid id %d for %s." % (id, unicode(cls)))
    obj.fromDom(node)
    return obj
