from WebStack.Generic import EndOfResponse

class Resource(object):
    def __init__(self, model):
        self.model = model
        self.priyomInterface = self.model.priyomInterface
        self.store = self.priyomInterface.store
        self.modelAutoSetup = True
        
    def setupModel(self):
        if "flags" in self.query:
            self.model.setCurrentFlags((flag for flag in self.query["flags"].split(",") if len(flag) != 0))
        else:
            self.model.setCurrentFlags([])
        if "distinct" in self.query:
            self.model.setDistinct(True)
        else:
            self.model.setDistinct(False)
        if "limit" in self.query:
            try:
                self.model.setLimit(int(self.query["limit"]))
            except ValueError:
                trans.set_response_code(400)
                return
        else:
            self.model.setLimit(None)
        if "offset" in self.query:
            try:
                self.model.setOffset(int(self.query["offset"]))
            except ValueError:
                trans.set_response_code(400)
                return
        else:
            self.model.setOffset(None)
            
    def normalizeQueryDict(self):
        for key in self.query.iterkeys():
            self.query[key] = self.query[key][0]
        
    def respond(self, trans):
        self.store.autoreload() # to make sure we get current data
        self.trans = trans
        self.out = trans.get_response_stream()
        self.query = trans.get_fields_from_path()
        self.normalizeQueryDict()
        self.setupModel()
        result = self.handle(trans)
        self.store.flush()
        return result
        
    def parameterError(self, parameterName, message = None):
        self.trans.set_response_code(400)
        print >>self.out, "Call error: Parameter error: %s%s" % (parameterName, " ("+message+")" if message is not None else "")
        raise EndOfResponse
        
    def getQueryInt(self, name, message = None):
        try:
            return int(self.query[name])
        except ValueError:
            self.parameterError(name, message)
        except KeyError:
            self.parameterError(name, message)
            
    def getQueryIntDefault(self, name, default, message = None):
        try:
            return int(self.query[name])
        except ValueError:
            self.parameterError(name, message)
        except KeyError:
            return default
