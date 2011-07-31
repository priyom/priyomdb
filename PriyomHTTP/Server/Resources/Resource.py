
class Resource(object):
    def __init__(self, model):
        self.model = model
        self.priyomInterface = self.model.priyomInterface
        self.store = self.priyomInterface.store
        
    def respond(self, trans):
        self.trans = trans
        self.out = trans.get_response_stream()
        return self.handle(trans)
