from libPriyom import *
from WebStack.Generic import ContentType, EndOfResponse
from Resource import Resource

class StationResource(Resource):
    def __init__(self, model):
        super(StationResource, self).__init__(model)
        
    def _getStation(self, trans, path):
        stationDesignator = path[1].decode("utf-8")
        if len(stationDesignator) == 0:
            return None
        self.priyomInterface.getStation(stationDesignator)
        
        
    def handle(self, trans):
        path = trans.get_virtual_path_info().split('/')
        if len(path) == 1:
            trans.set_response_code(404)
            return
        elif len(path) > 2:
            trans.set_response_code(404)
            return
            
        station = self._getStation(trans, path)        
        if station is None:
            trans.set_response_code(404)
            return
        station.validate()
        
        
        trans.set_content_type(ContentType("application/xml"))
        print >>self.out, self.model.exportToXml(station)

