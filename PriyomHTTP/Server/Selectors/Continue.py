from WebStack.Generic import EndOfResponse, ContentType
from Selector import Selector

class ContinueSelector(Selector):
    def __init__(self, resource):
        self.resource = resource
        
    def respond(self, trans):
        super(ContinueSelector, self).respond(trans)
        if not "100-continue" in self.getHeaderValuesSplitted("Expect"):
            return self.resource.respond(trans)
        else:
            #trans.rollback()
            #trans.set_response_code(417)
            #trans.set_content_type(ContentType("text/plain", "ascii"))
            # print >>self.out, u"We do not support 100-continue (its a WebStack issue afaik).".encode("ascii")
            trans.set_response_code(417)
            trans.set_content_type(ContentType("text/plain", "ascii"))
            print >>self.out, u"We do not support 100-continue (its a WebStack issue afaik).".encode("ascii")
            raise EndOfResponse
        
