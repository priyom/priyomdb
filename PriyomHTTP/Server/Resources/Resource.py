from WebStack.Generic import EndOfResponse

class Preference(object):
    def __init__(self, value, q):
        self.value = value
        self.q = q
    
    def __cmp__(self, other):
        if issubclass(type(other), Preference):
            return cmp(self.q, other.q)
        else:
            raise TypeError("Cannot compare {0} and {1}.".format(type(self), type(other)))
            
    def __str__(self):
        return "{0};q={1:.2f}".format(self.value, self.q)

class Resource(object):
    allowedMethods = frozenset(["HEAD", "GET"])
    
    def __init__(self, model):
        self.model = model
        self.priyomInterface = self.model.priyomInterface
        self.store = self.priyomInterface.store
        self.modelAutoSetup = True
        
    def parseCharsetPreferences(self, charsetPreferences):
        prefs = (s.lstrip().rstrip().lower().partition(';') for s in charsetPreferences.split(","))
        prefs = [Preference(charset, float(q[2:]) if len(q) > 0 else 1.0) for (charset, sep, q) in prefs if not (len(q) > 0 and float(q[2:])==0)]
        prefs.sort(reverse=True)        
        return prefs
        
    def getCharsetToUse(self, prefList, ownPreferences):
        use = None
        q = None
        if len(prefList) == 0:
            return ownPreference[0]
        for item in prefList:
            if q is None:
                q = item.q
            if use is None:
                use = item
            if item.q < q:
                break
            if item.value in ownPreferences:
                return item.value
            if item.value == "*" and use is None:
                use = ownPreferences[0]
        return use
        
    def parsePreferences(self, trans):
        prefs = self.parseCharsetPreferences(", ".join(trans.get_header_values("Accept-Charset")))
        charset = self.getCharsetToUse(prefs, ["utf-8", "utf8"])
        if charset is None:
            trans.rollback()
            trans.set_response_code(400)
            print >>trans.get_response_stream(), "user agent does not support any charsets"
        self.encoding = charset
        
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
        if not trans.get_request_method() in self.allowedMethods:
            trans.set_response_code(405)
            trans.set_header_value("Allow", ", ".join(self.allowedMethods))
            print >>trans.get_response_stream(), "Request method {0} is not allowed on this resource.".format(trans.get_request_method())
            raise EndOfResponse
        self.parsePreferences(trans)
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
        if lastModified is None:
            return
        if self.ifModifiedSinceUnix is not None and long(lastModified) == long(self.ifModifiedSinceUnix):
            self.trans.set_response_code(304)
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
