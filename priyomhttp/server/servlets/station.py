import baseServlet
from ..errors import ServletError, ServletInvalidQueryError, ServletMissingArgument
import libpriyom.interface
import libpriyom.stations
from ..servlets import register

class StationServlet(baseServlet.Servlet):
    def _writeStation(self, station, flags, httpRequest):
        doc = self.priyomInterface.exportToDom(station, flags)
        self.setHeader("Content-Type", "text/xml; charset=utf-8")
        httpRequest.wfile.write(doc.toxml().encode("UTF-8"))
    
    def getById(self, id, httpRequest, flags = None):
        station = self.store.get(libpriyom.stations.Station, id)
        if station is None:
            raise ServletError(404, "Station does not exist")
        
        self._writeStation(station, flags, httpRequest)
        
    def getByEnigmaId(self, enigmaId, httpRequest, flags = None):
        station = self.store.find(libpriyom.stations.Station, EnigmaIdentifier=enigmaId).any()
        if station is None:
            raise ServletError(404, "No station with this enigma identifier exists")
        
        self._writeStation(station, flags, httpRequest)
        
    def getByPriyomId(self, priyomId, httpRequest, flags = None):
        station = self.store.find(libpriyom.stations.Station, PriyomIdentifier=priyomId).any()
        if station is None:
            raise ServletError(404, "No station with this priyom identifier exists")
        
        self._writeStation(station, flags, httpRequest)
    
        
register("station", StationServlet, True, "station.py")
