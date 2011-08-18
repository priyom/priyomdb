from WebStack.Generic import ContentType
from libPriyom import *
from API import API

class ListModulationsAPI(API):
    def __init__(self, model):
        super(ListModulationsAPI, self).__init__(model)
    
    def handle(self, trans):
        super(ListModulationsAPI, self).handle(trans)
        
        items = self.store.find(Modulation)
        self.model.limitResults(items)
        
        trans.set_content_type(ContentType("application/xml"))
        
        doc = self.model.getExportDoc("priyom-modulations")
        rootNode = doc.documentElement
        for modulation in items:
            modulation.toDom(rootNode)
        print >>self.out, doc.toxml()

