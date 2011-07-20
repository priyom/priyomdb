import SocketServer
import BaseHTTPServer
import errors
import urllib
import os.path
import socket
import servlets
import cStringIO

class InvalidVersion(errors.ServletError):
    pass

class InvalidServletResponseError(errors.ServletError):
    pass

class PriyomHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = "PriyomHTTPd/0.3"
    
    exports = None
    def setHeader(self, key, value):
        self.responseHeaders[key] = value
    
    def checkVersion(self):
        if not (self.request_version in ["HTTP/1.0", "HTTP/1.1"]):
            raise InvalidVersion(400, "Bad request (version %s not supported)." % self.version )
            
    def handle_one_request(self):
        try:
            self.responseHeaders = {}
            self.raw_requestline = self.rfile.readline()
            if not self.raw_requestline:
                self.close_connection = 1
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return
            self.checkVersion()
            path, query = urllib.splitquery(urllib.splitattr(self.path)[0])
            segments = [unicode(urllib.unquote(x)) for x in path[1:].split('/')]
            
            prefixes = segments[:-1]
            command = segments[-1]
            
            commandSegments = command.split('.')
            if len(commandSegments) == 0 and len(prefixes) == 0:
                self.defaultResponse()
            else:
                arguments = {}
                if query is not None:
                    for arg in query.split('&'):
                        try:
                            key, value = arg.split("=", 1)
                            key = unicode(urllib.unquote(key))
                            value = unicode(urllib.unquote_plus(value))
                        except ValueError:
                            key = unicode(urllib.unquote(arg))
                            value = None
                            pass
                        arguments[key] = value
                getDoc = False
                httpCommand = self.command
                actualwfile = self.wfile
                self.wfile = cStringIO.StringIO()
                try:
                    wfile = self.wfile
                    rfile = self.rfile
                    if len(prefixes) == 1:
                        if prefixes[0] != "doc":            
                            raise errors.ServletError(400, "Bad request (This prefix is not supported).")
                        else:
                            getDoc = True
                    elif len(prefixes) > 1:
                        raise errors.ServletError(400, "Bad request (This prefix is not supported).")
                    
                    currExport = self.exports
                    if not (len(commandSegments) == 1 and commandSegments[0] == ""):
                        for segment in commandSegments:
                            if not segment in currExport:
                                raise errors.ServletUnknownCommand()
                            if getDoc or currExport.supports(httpCommand):
                                currExport = currExport[segment]
                            else:
                                raise errors.ServletUnsupportedMethod(httpCommand)
                    if getDoc:
                        if httpCommand != "GET":
                            raise errors.ServletError(400, "Invalid request method for doc/ prefix.")
                        self.setHeader("Content-Type", "text/html")
                        wfile.write('<html><head><title>%s</title></head><body>' % (str(currExport)))
                        html = currExport.html()
                        if "%s" in html:
                            html = html % (self.instanceName+"."+(".".join(commandSegments)))
                        wfile.write(html)
                        wfile.write('</body></html>')
                        message = None
                    else:
                        if not callable(currExport):
                            raise errors.ServletUnknownCommand()
                        message = currExport(self, arguments)
                finally:
                    responseData = self.wfile.getvalue()
                    self.wfile.close()
                    self.wfile = actualwfile
                
                # responseMessage, responseHeaders, responseData = servlet.serve(self.command, commandSegments, arguments, prefixes, self.rfile)
                self.send_response(200, message)
                for key, value in self.responseHeaders.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(responseData)
            self.wfile.flush() #actually send the response if not already done.
        except errors.ServletError as error:
            self.send_error(error.code, error.message)
        except socket.timeout, e:
            #a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = 1
            return
        #except Exception as error:
        #    self.send_error(500, str(error))

def _setupNamespaceNamesRecurse(namespace):
    for key, value in iter(namespace):
        value.fullPath = namespace.fullPath + "." + key
        _setupNamespaceNamesRecurse(value)
        
def setupNamespaceNames(namespace):
    for key, value in iter(namespace):
        value.fullPath = key
        _setupNamespaceNamesRecurse(value)
