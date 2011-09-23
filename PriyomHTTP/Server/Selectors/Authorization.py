from WebStack.Generic import EndOfResponse

class AuthorizationSelector(object):
    def __init__(self, resource, requiredCap):
        self.resource = resource
        self.requiredCap = requiredCap
        if type(self.requiredCap) != list:
            self.requiredCap = [self.requiredCap]
        
        self.title = self.resource.title
        if hasattr(self.resource, "shortDescription"):
            self.shortDescription = self.resource.shortDescription
        
    def respond(self, trans):
        for cap in self.requiredCap:
            if cap in trans.apiCaps:
                return self.resource.respond(trans)
        self.authFailed(trans)
        
    def doc(self, trans, breadcrumbs):
        # transparently pass this through
        return self.resource.doc(trans, breadcrumbs)
        
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
