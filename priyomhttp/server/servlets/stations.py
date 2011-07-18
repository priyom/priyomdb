from storm.locals import *
import baseServlet
from ..errors import ServletError, ServletInvalidQueryError
import libpriyom.interface
import libpriyom.stations
import libpriyom.helpers.selectors
from ..servlets import register

class StationsServlet(baseServlet.Servlet):
    def __init__(self, instanceName, priyomInterface):
        super(StationsServlet, self).__init__(instanceName, priyomInterface)
        self.finder = libpriyom.helpers.selectors.ObjectFinder(self.store, libpriyom.stations.Station)
    
    def _writeList(self, stations, httpRequest):
        doc = self.priyomInterface.createDocument("priyom-stations-export")
        rootNode = doc.documentElement
        for station in stations:
            station.toDom(rootNode, frozenset())
        httpRequest.setHeader("Content-Type", "text/xml; charset=utf-8")
        httpRequest.wfile.write(doc.toxml().encode("utf-8"))
    
    def listAll(self, httpRequest, **kwargs):
        stations = [station for station in self._limitResults(self.store.find(libpriyom.stations.Station), kwargs)]
        if len(stations) == 0:
            raise ServletError(404, "None of these stations exist")
        self._writeList(stations, httpRequest)
    
    def list(self, httpRequest, idList = None, strict = False, **kwargs):
        if idList is None:
            self.listAll(httpRequest, **kwargs)
            return
        stations = [station for station in self._limitResults(self.store.find(libpriyom.stations.Station, libpriyom.stations.Station.ID in idList), kwargs)]
        if len(stations) == 0:
            raise ServletError(404, "None of these stations exist")
        if strict and (len(stations) != len(idList)):
           raise ServletError(404, "Not all of these stations exist")
        
        self._writeList(stations, httpRequest)
                
    def find(self, field, operator, value, httpRequest, negate = False, **kwargs):
        try:
            resultSet = self._limitResults(self.finder.select(field, operator, value, negate), kwargs)
        except libpriyom.helpers.selectors.ObjectFinderError as e:
            raise ServletInvalidQueryError(str(e))
        stations = [station for station in resultSet]
        if len(stations) == 0:
            raise ServletError(404, "No stations match the given criteria")
        
        self._writeList(stations, httpRequest)
    
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

