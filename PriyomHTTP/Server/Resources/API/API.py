from WebStack.Generic import EndOfResponse
from ..Resource import Resource, CallSyntax, Argument

class API(Resource):
    def __init__(self, model):
        super(API, self).__init__(model)
