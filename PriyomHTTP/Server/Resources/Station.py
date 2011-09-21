from libPriyom import *
from WebStack.Generic import ContentType, EndOfResponse
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
            return None
        (lastModified, station) = self.priyomInterface.getStation(stationDesignator, notModifiedCheck=self.autoNotModified)
        if station is None:
            trans.set_response_code(404)
            return
        
        trans.set_header_value("Last-Modified", self.model.formatHTTPTimestamp(lastModified))
        trans.set_content_type(ContentType("application/xml", self.encoding))
        print >>self.out, self.model.exportToXml(station, encoding=self.encoding)

