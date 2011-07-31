from WebStack.Generic import ContentType
from Resource import Resource

class StationResource(Resource):
    def __init__(self, model):
        super(StationResource, self).__init__(model)
        self.firstCall = True
        
    def handle(self, trans):
        path = trans.get_virtual_path_info().split('/')
        if len(path) == 1:
            trans.set_response_code(404)
            return
        elif len(path) > 2:
            trans.set_response_code(404)
            return
        
        stationDesignator = path[1]
        try:
            stationId = int(stationDesignator)
        except ValueError:
            pass

