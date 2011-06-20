from storm.locals import *
import xmlintf

def importSimple(store, cls, node):
    idNode = xmlintf.getChild(node, "id")
    if idNode is None:
        return None
    id = int(idNode.childNodes[0].data)
    obj = None
    if id < 0:
        obj = cls()
        store.add(obj)
        print("added to store")
    else:
        obj = store.get(cls, id)
        if obj is None:
            raise ValueError("Invalid id %d for %s." % (id, unicode(cls)))
    print("calling fromDom")
    obj.fromDom(node)
    return obj
