from WebStack.Generic import ContentType
from libPriyom import *
from API import API

class ListStationsAPI(API):
    def handle(self, trans):
        super(ListStationsAPI, self).handle(trans)
        
        stations = self.store.find(Station)
        self.model.limitResults(stations)
        
        trans.set_content_type(ContentType("application/xml"))
        print >>self.out, self.model.exportListToXml(stations, Station)

