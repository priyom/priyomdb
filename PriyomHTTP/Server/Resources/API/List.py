from WebStack.Generic import ContentType
from libPriyom import *
from API import API

class ListAPI(API):
    def __init__(self, model, cls):
        super(ListAPI, self).__init__(model)
        self.cls = cls
    
    def handle(self, trans):
        super(ListAPI, self).handle(trans)
        
        items = self.store.find(self.cls)
        self.model.limitResults(items)
        
        trans.set_content_type(ContentType("application/xml"))
        print >>self.out, self.model.exportListToXml(items, self.cls)

