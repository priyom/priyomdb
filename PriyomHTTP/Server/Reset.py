class ResetSelector(object):
    def __init__(self, model, child):
        self.model = model
        self.child = child
        
    def respond(self, trans):
        self.model.checkReset()
        return self.child.respond(trans)
