import baseServlet
from ..errors import ServletError, ServletInvalidQueryError
import libpriyom.interface
from libpriyom.broadcasts import Broadcast
from ..servlets import register

class BroadcastServlet(baseServlet.Servlet):
    def _writeBroadcast(self, broadcast, flags, httpRequest):
        doc = self.priyomInterface.exportToDom(broadcast, flags)
        httpRequest.setHeader("Content-Type", "text/xml; charset=utf-8")
        httpRequest.wfile.write(doc.toxml().encode("UTF-8"))
    
    def getById(self, id, httpRequest, flags = frozenset()):
        broadcast = self.store.get(Broadcast, id)
        if broadcast is None:
            raise ServletError(404, "Broadcast does not exist")
        
        self._writeBroadcast(broadcast, flags, httpRequest)

register("broadcast", BroadcastServlet, True, "broadcast.py")
