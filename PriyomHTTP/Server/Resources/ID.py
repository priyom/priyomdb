from libPriyom import *
from WebStack.Generic import ContentType
from Resource import Resource

class IDResource(Resource):
    def __init__(self, model, classType):
        super(IDResource, self).__init__(model)
        self.classType = classType
        
    def handle(self, trans):
        path = trans.get_virtual_path_info().split('/')
        if len(path) == 1:
            trans.set_response_code(404)
            return
        elif len(path) > 2:
            trans.set_response_code(404)
            return
        
        try:
            objId = int(path[1].decode("utf-8"))
        except ValueError:
            trans.set_response_code(404)
            return
        obj = self.store.get(self.classType, objId)
        if obj is None:
            trans.set_response_code(404)
            return
        obj.validate()
        self.autoNotModified(obj.Modified)
        
        trans.set_header_value("Last-Modified", self.model.formatHTTPTimestamp(obj.Modified))
        trans.set_content_type(ContentType("application/xml", self.encoding))
        print >>self.out, self.model.exportToXml(obj, encoding=self.encoding)


