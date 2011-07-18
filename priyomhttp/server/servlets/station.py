import baseServlet
from errors import ServletError, ServletInvalidQueryError
import libpriyom.interface
import libpriyom.stations
from ..servlets import register

class StationServlet(baseServlet.Servlet):
    def _writeStation(self, station, arguments, wfile):
        doc = self.priyomInterface.exportToDom(station, flags=frozenset((key for key, value in arguments.items() if value == u"1")))
        self.setHeader("Content-Type", "text/xml; charset=utf-8")
        wfile.write(doc.toxml().encode("UTF-8"))
    
    def getById(self, pathSegments, arguments, rfile, wfile):
        if len(pathSegments) != 1:
            raise ServletInvalidQueryError()
        try:
            id = int(pathSegments[0])
        except ValueError:
            raise ServletInvalidQueryError("Non-integer id given")
        station = self.store.get(libpriyom.stations.Station, id)
        if station is None:
            raise ServletError(404, "Station does not exist")
        
        self._writeStation(station, arguments, wfile)
        
    def getByEnigma(self, pathSegments, arguments, rfile, wfile):
        if len(pathSegments) != 1:
            raise ServletInvalidQueryError()
        station = self.store.find(libpriyom.stations.Station, EnigmaIdentifier=pathSegments[0]).any()
        if station is None:
            raise ServletError(404, "No station with this enigma identifier exists")
        
        self._writeStation(station, arguments, wfile)
        
    def getByPriyom(self, pathSegments, arguments, rfile, wfile):
        if len(pathSegments) != 1:
            raise ServletInvalidQueryError()
        station = self.store.find(libpriyom.stations.Station, PriyomIdentifier=pathSegments[0]).any()
        if station is None:
            raise ServletError(404, "No station with this priyom identifier exists")
        
        self._writeStation(station, arguments, wfile)
    
    def do_GET(self, pathSegments, arguments, rfile, wfile):
        try:
            id = int(pathSegments[0])
        except ValueError:
            try:
                method = {
                    "id": self.getById,
                    "enigma": self.getByEnigma,
                    "priyom": self.getByPriyom
                }[pathSegments[0]]
            except KeyError:
                raise ServletInvalidQueryError("Invalid selector")
            return method(pathSegments[1:], arguments, rfile, wfile)
        self.getById(pathSegments, arguments, rfile, wfile)

register("station", StationServlet, True, "station.py")
