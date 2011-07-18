import SocketServer
import BaseHTTPServer
import servlets
import urllib
import os.path

class InvalidServletResponseError(Exception):
    pass

class PriyomHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = "PriyomHTTPd/0.1.1"
    
    def checkVersion(self):
        if self.request_version == "HTTP/0.9":
            self.send_error(400, "Bad request (version %s not supported)." % self.version )
            return False
        else:
            return True
    
    def do_GET(self):
        if not self.checkVersion():
            return
        path, query = urllib.splitquery(urllib.splitattr(self.path)[0])
        segments = [unicode(urllib.unquote(x)) for x in path.split('/')]
        servlet = servlets.get(segments[1])
        if servlet is None:
            self.send_error(404, "Unknown servlet \"%s\" requested." % segments[1])
            return
        arguments = {}
        if query is not None:
            for arg in query.split('&'):
                try:
                    key, value = arg.split("=", 1)
                    key = unicode(urllib.unquote(key))
                    value = unicode(urllib.unquote_plus(value))
                except ValueError:
                    key = unicode(urllib.unquote(arg))
                    value = u"1"
                    pass
                arguments[key] = value
            
        responseCode, responseHeaders, responseMessage = servlet.serve("GET", segments[2:], arguments, self.rfile)
        if responseCode[0] < 200 or responseCode[0] >= 600:
            raise InvalidServletResponseError("%d is an invalid servlet response code.")
        elif responseCode[0] >= 200 and responseCode[0] < 300:
            self.send_response(responseCode[0], responseCode[1])
            for key, value in responseHeaders.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(responseMessage)
        elif responseCode[0] >= 300:
            self.send_error(responseCode[0], responseCode[1])
