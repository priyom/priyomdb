class WebModel(object):
    def __init__(self, priyomInterface):
        self.priyomInterface = priyomInterface
        self.store = self.priyomInterface.store
    
    def exportToXml(self, obj, flags = None):
        return self.priyomInterface.exportToDom(obj, flags).toxml()
