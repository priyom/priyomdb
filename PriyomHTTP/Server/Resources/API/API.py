from WebStack.Generic import EndOfResponse
from ..Resource import Resource

class API(Resource):
    def __init__(self, model):
        super(API, self).__init__(model)
        
    def unsupportedMethod(self):
        trans.set_response_code(405)
        raise EndOfResponse
        
    def handle(self, trans):
        if not (trans.get_request_method() in ["GET", "HEAD"]):
            self.unsupportedMethod()
        self.head = (trans.get_request_method() == "HEAD")
