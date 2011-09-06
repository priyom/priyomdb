class MyEncodingSelector(object):

    def __init__(self, resource, encoding):
        self.resource = resource
        self.encoding = encoding

    def respond(self, trans):
        trans.default_charset = self.encoding
        self.resource.respond(trans)
        if not ("charset" in trans.content_type.attributes):
            trans.content_type.attributes["charset"] = self.encoding

