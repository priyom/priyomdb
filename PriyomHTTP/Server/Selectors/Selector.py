class Selector(object):
    def getHeaderValuesSplitted(self, headerName):
        return [s.lstrip().rstrip() for s in ",".join(self.trans.get_header_values(headerName)).split(",")]
    
    def respond(self, trans):
        self.trans = trans
        self.out = trans.get_response_stream()
