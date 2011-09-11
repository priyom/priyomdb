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
        ifModifiedSince = trans.get_header_values("If-Modified-Since")
        if len(ifModifiedSince) > 0:
            try:
                self.ifModifiedSince = self.model.parseHTTPDate(ifModifiedSince[-1])
            except ValueError as e:
                trans.set_response_code(400)
                print >>self.out, "If-Modified-Since date given in a invalid format: %s" % str(e)
                raise EndOfResponse
            self.ifModifiedSinceUnix = self.priyomInterface.toTimestamp(self.ifModifiedSince)
        else:
            self.ifModifiedSince = None
            self.ifModifiedSinceUnix = None
        self.normalizeQueryDict()
        self.setupModel()
        self.head = trans.get_request_method() == "HEAD"
        try:
            result = self.handle(trans)
        finally:
            self.store.flush()
        return result
        
    def parameterError(self, parameterName, message = None):
        self.trans.set_response_code(400)
        print >>self.out, "Call error: Parameter error: %s%s" % (parameterName, " ("+message+")" if message is not None else "")
        raise EndOfResponse
        
    def autoNotModified(self, lastModified):
        if self.ifModifiedSinceUnix is not None and long(lastModified) != long(self.ifModifiedSinceUnix):
            self.trans.set_response_code(304)
            return EndOfResponse
        
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
