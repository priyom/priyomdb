import baseServlet
from baseServlet import ServletError, ServletInvalidQueryError
import libpriyom.interface
from libpriyom.broadcasts import Broadcast
from ..servlets import register

class BroadcastServlet(baseServlet.Servlet):
    def _writeBroadcast(self, broadcast, arguments, wfile):
        doc = self.priyomInterface.exportToDom(broadcast, flags=frozenset((key for key, value in arguments.items() if value == u"1")))
        self.setHeader("Content-Type", "text/xml; charset=utf-8")
        wfile.write(doc.toxml().encode("UTF-8"))
    
    def getById(self, pathSegments, arguments, rfile, wfile):
        if len(pathSegments) != 1:
            raise ServletInvalidQueryError()
        try:
            id = int(pathSegments[0])
        except ValueError:
            raise ServletInvalidQueryError("Non-integer id given")
        broadcast = self.store.get(Broadcast, id)
        if broadcast is None:
            raise ServletError(404, "Broadcast does not exist")
        
        self._writeBroadcast(broadcast, arguments, wfile)
    
    def do_GET(self, pathSegments, arguments, rfile, wfile):
        try:
            id = int(pathSegments[0])
        except ValueError:
            try:
                method = {
                    "id": self.getById
                }[pathSegments[0]]
            except KeyError:
                raise ServletInvalidQueryError("Invalid selector")
            return method(pathSegments[1:], arguments, rfile, wfile)
        self.getById(pathSegments, arguments, rfile, wfile)

register("broadcast", BroadcastServlet, True, "broadcast.py")
