from WebStack.Generic import ContentType
from libPriyom import *
from API import API

class ListAPI(API):
    def __init__(self, model, cls):
        super(ListAPI, self).__init__(model)
        self.cls = cls
    
    def handle(self, trans):
        lastModified, items = self.priyomInterface.listObjects(self.cls, limiter=self.model, notModifiedCheck=self.autoNotModified, head=self.head)
        trans.set_content_type(ContentType("application/xml"))
        trans.set_header_value("Last-Modified", self.model.formatHTTPTimestamp(float(lastModified)))
        if self.head:
            return
        
        
        print >>self.out, self.model.exportListToXml(items, self.cls)

