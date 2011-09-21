from WebStack.Generic import EndOfResponse

class ContinueSelector(object):
    def __init__(self, resource):
        self.resource = resource
        
    def respond(self, trans):
        if ", ".join(trans.get_header_values("Expect").split(",")
