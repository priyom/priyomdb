from WebStack.Generic import ContentType
from cfg_priyomhttpd import application, doc, misc

class DocumentationSelector(object):
    path_encoding = "utf-8"
    
    def __init__(self, resource):
        self.resource = resource
    
    def respond(self, trans):
        if hasattr(self.resource, "doc"):
            trans.encoding = "utf-8"
            breadcrumbs = None
            if doc.get("breadcrumbs", {}).get("enabled", False):
                breadcrumbs = list()
            return self.resource.doc(trans, breadcrumbs)
        else:
            trans.rollback()
            trans.set_response_code(501)
            trans.set_content_type(ContentType("text/plain", "utf-8"))
            print >>trans.get_response_stream(), u"Documentation not implemented.".encode("utf-8")
