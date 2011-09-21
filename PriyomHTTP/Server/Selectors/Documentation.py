from WebStack.Generic import ContentType

class DocumentationSelector(object):
    def __init__(self, resource):
        self.resource = resource
    
    def respond(self, trans):
        if hasattr(self.resource, "doc"):
            trans.encoding = "utf-8"
            return self.resource.doc(trans)
        else:
            trans.rollback()
            trans.set_response_code(501)
            trans.set_content_type(ContentType("text/plain", "utf-8"))
            print >>trans.get_response_stream(), u"Documentation not implemented.".encode("utf-8")
