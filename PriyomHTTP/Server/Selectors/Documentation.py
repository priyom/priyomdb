
class DocumentationSelector(object):
    def __init__(self, resource):
        self.resource = resource
    
    def respond(self, trans):
        trans.set_response_code(500)
