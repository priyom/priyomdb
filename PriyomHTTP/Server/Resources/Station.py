from libPriyom import *
from WebStack.Generic import ContentType
from Resource import Resource

class StationResource(Resource):
    def __init__(self, model):
        super(StationResource, self).__init__(model)
        
    def handle(self, trans):
        path = trans.get_virtual_path_info().split('/')
        if len(path) == 1:
            trans.set_response_code(404)
            return
        elif len(path) > 2:
            trans.set_response_code(404)
            return
        
        stationDesignator = path[1].decode("utf-8")
        if len(stationDesignator) == 0:
            trans.set_response_code(404)
            return
        
        try:
            stationId = int(stationDesignator)
        except ValueError:
            stationId = None
        if stationId is not None:
            station = self.store.get(Station, stationId)
        else:
            resultSet = self.store.find(Station, Station.EnigmaIdentifier == stationDesignator)
            station = resultSet.any()
            if station is None:
                resultSet = self.store.find(Station, Station.PriyomIdentifier == stationDesignator)
            station = resultSet.any()
        
        if station is None:
            trans.set_response_code(404)
            return
        
        trans.set_content_type(ContentType("application/xml"))
        print >>self.out, self.model.exportToXml(station)

