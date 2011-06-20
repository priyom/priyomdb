import cStringIO

class ServletError(Exception):
    def __init__(self, code, message=None):
        self.code = code
        self.message = message
        
class ServletInvalidQueryError(ServletError):
    def __init__(self, message = "Invalid query"):
        super(ServletInvalidQueryError, self).__init__(404, message)

class Servlet(object):
    def __init__(self, instanceName, priyomInterface):
        self.instanceName = instanceName
        self.priyomInterface = priyomInterface
        self.store = self.priyomInterface.store
        
    def _limitResults(self, resultSet, arguments):
        offset = None
        try:
            offset = int(arguments["offset"])
        except KeyError:
            pass
        except ValueError:
            pass
        limit = None
        try:
            limit = int(arguments["limit"])
        except KeyError:
            pass
        except ValueError:
            pass
        distinct = "distinct" in arguments and arguments["distinct"] == u"1"
        resultSet.config(distinct, offset, limit)
        return resultSet
        
    def setReplyCode(self, code, message = None):
        self.code = code
        self.message = message
        
    def setHeader(self, key, value):
        self.headers[key] = value
        
    def unsetHeader(self, key):
        try:
            del self.headers[key]
        except KeyError:
            pass
            
    def do_GET(self, pathSegments, arguments, rfile, wfile):
        self.setHeader("ContentType", "text/plain")
        wfile.write(u"command: %s\n" % command)
        wfile.write(u"call path segments:\n")
        for segment in pathSegments:
            wfile.write(u"  %s\n" % segment)
        wfile.write(u"call path attributes:\n")
        for key, value in arguments.items():
            wfile.write(u"  %s=%s\n" % (key, value))

        wfile.write(u"servlet instance: %s; this servlet does not contain any code" % self.instanceName)

    
    def doService(self, command, pathSegments, arguments, rfile, wfile):
        try:
            method = getattr(self, "do_"+command)
        except AttributeError:
            self.setReplyCode(400, "Invalid request command.")
        try:
            method(pathSegments, arguments, rfile, wfile)
        except ServletError as error:
            self.setReplyCode(error.code, error.message)
        
    def serve(self, command, pathSegments, arguments, rfile):
        self.code = 200
        self.message = None
        self.headers = {}
        
        wfile = cStringIO.StringIO()
        self.doService(command, pathSegments, arguments, rfile, wfile)
        data = wfile.getvalue()
        wfile.close()
        return (self.code, self.message), self.headers, data
