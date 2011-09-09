from WebStack.Generic import EndOfResponse

class AuthorizationSelector(object):
    def __init__(self, resource, requiredCap):
        self.resource = resource
        self.requiredCap = requiredCap
        
    def respond(self, trans):
        if not (self.requiredCap in trans.apiCaps):
            self.authFailed(trans)
        return self.resource.respond(trans)
        
    def authFailed(self, trans):
        trans.set_response_code(401)
        if not trans.apiAuth:
            if trans.apiAuthError is not None:
                print >>trans.get_response_stream(), trans.apiAuthError
            else:
                print >>trans.get_response_stream(), "Not authenticated."
        else:
            print >>trans.get_response_stream(), "Missing capabilities."
        raise EndOfResponse
