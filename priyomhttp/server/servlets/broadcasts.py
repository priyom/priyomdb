from ..limits import queryLimits
from storm.locals import *
import baseServlet
from ..errors import ServletError, ServletInvalidQueryError
import libpriyom.interface
from libpriyom.stations import Station
from libpriyom.broadcasts import Broadcast, BroadcastFrequency
from libpriyom.modulations import Modulation
import libpriyom.helpers.selectors
from ..servlets import register
import time, datetime

class BroadcastsServlet(baseServlet.Servlet):
    def __init__(self, instanceName, priyomInterface):
        super(BroadcastsServlet, self).__init__(instanceName, priyomInterface)
        self.finder = libpriyom.helpers.selectors.ObjectFinder(self.store, Broadcast)

    def _now(self):
        return int(time.mktime(datetime.datetime.utcnow().timetuple()))
        
    def _writeList(self, broadcasts, flags, httpRequest):
        doc = self.priyomInterface.createDocument("priyom-broadcasts-export")
        rootNode = doc.documentElement
        for broadcast in broadcasts:
            broadcast.toDom(rootNode, flags)
        httpRequest.setHeader("Content-Type", "text/xml; charset=utf-8")
        httpRequest.wfile.write(doc.toxml().encode("utf-8"))
        
    def getUpcoming(self, httpRequest, timeLimit = None, update = True, all = False, stationId = None, flags = frozenset(), **kwargs):
        responseMessage = None
        maxTimeRange = queryLimits.broadcasts.maxTimeRangeForUpdatingQueries if stationId is None else queryLimits.broadcasts.maxTimeRangeForStationBoundUpdatingQueries
        
        if timeLimit is None:
            timeLimit = maxTimeRange # automatically set
        
        now = self._now()
        if update:
            untilDate = datetime.datetime.fromtimestamp(now)
            untilDate += datetime.timedelta(seconds=timeLimit)
            untilDate = datetime.datetime(year=untilDate.year, month=untilDate.month, day=untilDate.day)
            until = int(time.mktime(untilDate.timetuple()))
            if stationId is None:
                validUntil = self.priyomInterface.scheduleMaintainer.updateSchedules(until, maxTimeRange)
            else:
                station = self.store.get(Station, stationId)
                if station is None:
                    raise ServletError(404, "Station does not exist (no update query possible)")
                validUntil = self.priyomInterface.scheduleMaintainer.updateSchedule(station, until, maxTimeRange)
            if validUntil < until:
                responseMessage = "Information may be out of date"
            httpRequest.setHeader("Expires", self.formatTimestamp(validUntil))
        
        where = And(Or(Broadcast.BroadcastEnd > now, Broadcast.BroadcastEnd == None), (Broadcast.BroadcastStart < (now + timeLimit)))
        if not all:
            where = And(where, Broadcast.Type == u"data")
        if stationId is not None:
            where = And(where, Broadcast.StationID == stationId)
        
        resultSet = self.store.find(Broadcast, where)
        self._limitResults(resultSet, kwargs)
        broadcasts = [broadcast for broadcast in resultSet]
        if len(broadcasts) == 0:
            raise ServletError(404, "No upcoming %sbroadcasts within the next %d seconds" % ("" if all else "data (you may want to try the \"all\" flag) ", timeLimit))
        
        self._writeList(broadcasts, flags, httpRequest)
        return responseMessage
        
    def getByFrequency(self, frequency, httpRequest, jitter = 0, modulation = None, flags = frozenset(), **kwargs):
        if type(frequency) == tuple:
            minFreq = frequency[0]
            maxFreq = frequency[1]
        else:
            minFreq = frequency
            maxFreq = frequency
        
        where = And(And(And(BroadcastFrequency.BroadcastID == Broadcast.ID, BroadcastFrequency.ModulationID == Modulation.ID), BroadcastFrequency.Frequency >= minFreq), BroadcastFrequency.Frequency <= maxFreq)
        if modulation is not None:
            where = And(where, Modulation.Name == modulation)
        
        resultSet = self._limitResults(self.store.find((Broadcast, BroadcastFrequency, Modulation), where), kwargs)
        #if resultSet.count() > 100:
        #    raise ServletError(500, "Too many results (try to use ?limit= and ?offset=)")
        self._writeList((broadcast for broadcast, frequency, modulation in resultSet), flags, httpRequest)
        
    def listForStation(self, stationId, httpRequest, flags = frozenset(), **kwargs):
        resultSet = self._limitResults(self.store.find(Broadcast, Broadcast.StationID == stationId), kwargs)
        self._writeList((broadcast for broadcast in resultSet), flags, httpRequest)
        
    def find(self, field, operator, value, httpRequest, negate = False, **kwargs):
        try:
            resultSet = self._limitResults(self.finder.select(field, operator, value, negate), kwargs)
        except libpriyom.helpers.selectors.ObjectFinderError as e:
            raise ServletInvalidQueryError(str(e))
        broadcasts = [broadcast for broadcast in resultSet]
        if len(broadcasts) == 0:
            raise ServletError(404, "No stations match the given criteria")
        
        self._writeList(broadcasts, frozenset(), httpRequest)


register("broadcasts", BroadcastsServlet, True, "broadcasts.py")
