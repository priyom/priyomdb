from storm.locals import *
import baseServlet
from errors import ServletError, ServletInvalidQueryError
import libpriyom.interface
import libpriyom.stations
import libpriyom.helpers.selectors
from ..servlets import register

class StationsServlet(baseServlet.Servlet):
    def __init__(self, instanceName, priyomInterface):
        super(StationsServlet, self).__init__(instanceName, priyomInterface)
        self.finder = libpriyom.helpers.selectors.ObjectFinder(self.store, libpriyom.stations.Station)
    
    def _writeList(self, stations, wfile):
        doc = self.priyomInterface.createDocument("priyom-stations-export")
        rootNode = doc.documentElement
        for station in stations:
            station.toDom(rootNode, frozenset())
        self.setHeader("Content-Type", "text/xml; charset=utf-8")
        wfile.write(doc.toxml().encode("utf-8"))
    
    def doListAll(self, arguments, wfile):
        stations = [station for station in self._limitResults(self.store.find(libpriyom.stations.Station), arguments)]
        if len(stations) == 0:
            raise ServletError(404, "None of these stations exist")
        self._writeList(stations, wfile)
    
    def doList(self, pathSegments, arguments, wfile):
        if len(pathSegments) == 0 or len(pathSegments[0]) == 0:
            self.doListAll(arguments, wfile)
            return
        if len(pathSegments) > 1:
            raise ServletInvalidQueryError()
        try:
            idList = [int(i) for i in pathSegments[0].split(",")]
        except ValueError:
            raise ServletInvalidQueryError()
        stations = [station for station in self._limitResults(self.store.find(libpriyom.stations.Station, libpriyom.stations.Station.ID in idList), arguments)]
        if len(stations) == 0:
            raise ServletError(404, "None of these stations exist")
        if "strict" in arguments and (len(stations) != len(idList)):
           raise ServletError(404, "Not all of these stations exist")
        
        self._writeList(stations, wfile)
                
    def doFind(self, pathSegments, arguments, wfile):
        if not (len(pathSegments) == 4 and pathSegments[1] == "not") and not len(pathSegments) == 3:
            raise ServletInvalidQueryError("Invalid argument count")
        negate = False
        if pathSegments[1] == "not":
            negate = True
            operand = pathSegments[2]
            value = pathSegments[3]
        else:
            operand = pathSegments[1]
            value = pathSegments[2]
        try:
            resultSet = self._limitResults(self.finder.select(pathSegments[0], operand, value, negate), arguments)
        except libpriyom.helpers.selectors.ObjectFinderError as e:
            raise ServletInvalidQueryError(str(e))
        stations = [station for station in resultSet]
        if len(stations) == 0:
            raise ServletError(404, "No stations match the given criteria")
        
        self._writeList(stations, wfile)
    
    def do_GET(self, pathSegments, arguments, rfile, wfile):
        try:
            method = {
                "list": self.doList,
                "find": self.doFind
            }[pathSegments[0]]
        except KeyError:
            raise ServletInvalidQueryError(404, "Invalid query")
        method(pathSegments[1:], arguments, wfile)

register("stations", StationsServlet, True, "stations.py")

