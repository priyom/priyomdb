import SocketServer
import BaseHTTPServer
import servlets
import servlets.errors
import urllib
import os.path
import socket

class InvalidVersion(servlets.errors.ServletError):
    pass

class InvalidServletResponseError(servlets.errors.ServletError):
    pass

class PriyomHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = "PriyomHTTPd/0.1.1"
    
    def checkVersion(self):
        if not (self.request_version in ["HTTP/1.0", "HTTP/1.1"]):
            raise InvalidVersion(400, "Bad request (version %s not supported)." % self.version )
            
    def handle_one_request(self):
        try:
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
            elif len(commandSegments) <= 1:
                raise ServletError(404, "No command specified")
            else:
                servletName = commandSegments[0]
                commandSegments = commandSegments[1:]
                servlet = servlets.get(servletName)
                if servlet is None:
                    raise servlets.errors.ServletError(404, "Unknown servlet: %r" % servletName)
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
                responseMessage, responseHeaders, responseData = servlet.serve(self.command, commandSegments, arguments, prefixes, self.rfile)
                self.send_response(200, responseMessage)
                for key, value in responseHeaders.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(responseData)
            self.wfile.flush() #actually send the response if not already done.
        except servlets.errors.ServletError as error:
            self.send_error(error.code, error.message)
        except socket.timeout, e:
            #a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = 1
            return
