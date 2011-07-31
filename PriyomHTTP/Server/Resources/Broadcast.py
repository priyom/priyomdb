from libPriyom import *
from WebStack.Generic import ContentType
from Resource import Resource

class BroadcastResource(Resource):
    def __init__(self, model):
        super(BroadcastResource, self).__init__(model)
        self.firstCall = True
        
    def handle(self, trans):
        path = trans.get_virtual_path_info().split('/')
        if len(path) == 1:
            trans.set_response_code(404)
            return
        elif len(path) > 2:
            trans.set_response_code(404)
            return
        
        try:
            broadcastId = int(path[1].decode("utf-8"))
        except ValueError:
            trans.set_response_code(404)
            return
        broadcast = self.store.get(Broadcast, broadcastId)
        
        if broadcast is None:
            trans.set_response_code(404)
            return
        
        trans.set_content_type(ContentType("application/xml"))
        print >>self.out, self.model.exportToXml(broadcast)


