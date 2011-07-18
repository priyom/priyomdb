import cStringIO
import time
import datetime
import errors

class Servlet(object):
    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    monthname = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
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
            
    def formatDate(self, dt):
        return dt.strftime("%%s, %d %%s %Y %T UTC") % (Servlet.weekdayname[dt.weekday()], Servlet.monthname[dt.month])
        
    def formatTimestamp(self, timestamp):
        return self.formatDate(datetime.datetime.fromtimestamp(timestamp))
        
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
        except errors.ServletError as error:
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
