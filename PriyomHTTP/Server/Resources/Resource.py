from WebStack.Generic import EndOfResponse, ContentType
from cfg_priyomhttpd import response, doc, misc, application

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
    title = u"untitled"
    
    def __init__(self, model):
        self.model = model
        self.priyomInterface = self.model.priyomInterface
        self.store = self.priyomInterface.store
        self.modelAutoSetup = True
        
    def parseCharsetPreferences(self, charsetPreferences):
        prefs = (s.lstrip().rstrip().lower().partition(';') for s in charsetPreferences.split(","))
        prefs = [Preference(charset, float(q[2:]) if len(q) > 0 else 1.0) for (charset, sep, q) in prefs if not (len(q) > 0 and float(q[2:])==0) and len(charset) > 0]
        prefs.sort(reverse=True)        
        return prefs
        
    def getCharsetToUse(self, prefList, ownPreferences):
        use = None
        q = None
        if len(prefList) == 0:
            return ownPreferences[0]
        for item in prefList:
            if q is None:
                q = item.q
            if use is None:
                use = item.value
            if item.q < q:
                break
            if item.value in ownPreferences:
                return item.value
            if item.value == "*" and use is None:
                use = ownPreferences[0]
        if use is None:
            use = ownPreferences[0]
        return use
        
    def parsePreferences(self, trans):
        prefs = self.parseCharsetPreferences(", ".join(trans.get_header_values("Accept-Charset")))
        charset = self.getCharsetToUse(prefs, response.get("defaultEncodings") or ["utf-8", "utf8"])
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
        
    def doc(self, trans, breadcrumbs):
        self.out = trans.get_response_stream()
        
        breadcrumbs = None
        
        docSubstitute = self.handleDocSubstitute if hasattr(self, "handleDocSubstitute") else u"No further documentation available."
        
        trans.set_response_code(200)
        trans.set_content_type(ContentType("text/html", "utf-8"))
        print >>self.out, u"""<html>
    <head>
        <title>{0}{1}{2}</title>
    </head>
    <body>
        <h1>Documentation</h1>"""+(u"""
        <div class="doc-breadcrumbs">{3}</div>""" if breadcrumbs is not None else u"")+u"""
        <h2>{0}</h2>
        <p>{4}</p>
        {5}
    </body>
</html>""".format(
            self.title,
            (misc.get("titleSeparator", u" ") + application["name"] + u" documentation") if "name" in application else u"",
            (misc.get("titleSeparator", u" ") + application["host"]) if "host" in application else u"",
            u"",
            self.shortDescription if hasattr(self, "shortDescription") else u"",
            self.handleDoc() or docSubstitute if hasattr(self, "handleDoc") else docSubstitute
        ).encode("utf-8")
        
    def handleDoc(self):
        result = u""
        if hasattr(self, "docArgs") and hasattr(self, "docCallSyntax") and hasattr(self, "docReturnValue"):
            result = result + u"""
<h3>Call syntax</h3>
<p>{0}</p>
<h3>Arguments</h3>
<table class="doc-arguments">
    <thead>
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
{1}
    </tbody>
</table>
<h3>Return value</h3>
{2}""".format(
                unicode(self.callSyntax),
                "\n".join((arg.docRowUnicode() for arg in self.docArgs)),
                unicode(self.returnValue)
            )
        if len(result) == 0:
            return None
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
