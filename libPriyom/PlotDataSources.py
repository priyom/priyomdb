from storm.locals import *
from storm.expr import *
from Transmission import Transmission
from Broadcast import Broadcast
from Station import Station
from Helpers import TimeUtils
import itertools

__all__ = ['PlotDataSource', 'PlotDataPunch', 'PlotDataWeekHourPunch', 'PlotDataMonthHourPunch', 'PlotDataUptime']

class PlotDataSource(object):
    def __init__(self, store):
        self.store = store
        
    def getLastModified(self, **kwargs):
        return 0
        
    def getData(self, *args, **kwargs):
        pass
        
class PlotDataUptime(PlotDataSource):
    height = 7
    width = 12.5
    
    xborder_left = 0.07
    xborder_right = 0.01
    yborder_bottom = 0.14
    yborder_top = 0.03
    
    def getLastModified(self, stationId = None, **kwargs):
        if stationId is None or stationId == 0:
            return max(
                        self.store.find(Broadcast, Broadcast.BroadcastEnd != None).max(Broadcast.Modified),
                        self.store.find(Station).max(Station.BroadcastRemoved),
                        self.store.find(Station).max(Station.Modified))
        else:
            return max(
                        self.store.find(Broadcast,
                            Broadcast.StationID == stationId,
                            Broadcast.BroadcastEnd != None).max(Broadcast.Modified),
                        self.store.get(Station, stationId).BroadcastRemoved,
                        self.store.get(Station, stationId).Modified)
            
    def _splitData(self, data):
        prevStation = None
        l = None
        for item in data:
            if prevStation != item[0]:
                if l is not None:
                    yield (prevStation, l)
                l = list()
                prevStation = item[0]
            l.append(item[1:])
            
    def _getMonthList(self, data):
        mapping = dict()
        prevMonth = None
        for stationItem in data:
            for monthItem in stationItem[1]:
                t = (monthItem[0], monthItem[1]-1)
                if not t in mapping:
                    mapping[t] = None
        
        keys = [(t, float(t[0])+float(t[1])/12.) for t in mapping.iterkeys()]
        keys.sort(key=lambda x: x[1])
        for t, v in keys:
            if prevMonth is not None:
                for year in xrange(prevMonth[0], t[0]+1):
                    minMonth = 0 if year > prevMonth[0] else prevMonth[1]+1
                    maxMonth = 12 if year < t[0] else t[1]
                    if minMonth == 12:
                        continue
                    if maxMonth < 0:
                        continue
                    for month in xrange(minMonth, maxMonth):
                        yield (year, month)
            yield t
            prevMonth = t
        
    def _mapData(self, data, monthList):
        monthList = [((year, month), 0) for year, month in monthList]
        
        for stationItem in data:
            station = stationItem[0]
            newStationData = dict(monthList)
            for monthItem in stationItem[1]:
                t = (monthItem[0], monthItem[1]-1)
                newStationData[t] = float(monthItem[2])
            yield (station, [(year, month, duration) for (year, month), duration in sorted(newStationData.iteritems(), key=lambda x: float(x[0][0])+float(x[0][1])/12.)])
            
    def _filterTicksExt(self, list, reference):
        yield list[0]
        for item, ref in itertools.izip(list[1:-1], reference[1:-1]):
            month = ref[1]
            if not month in (0, 3, 6, 9):
                continue
            yield item
        yield list[-1]
                        
    def getData(self, stationId = None, 
            years=None,
            **kwargs):
        if stationId == 0:
            stationId = None
        where = Broadcast.BroadcastEnd != None
        if stationId is not None:
            where = And(where, Broadcast.StationID == stationId)
        if years is not None:
            now = TimeUtils.nowDate()
            where = And(where, Broadcast.BroadcastStart >= TimeUtils.toTimestamp(datetime(year=now.year-years, month=now.month, day=1)))
        data = self.store.find(
            (
                Station,
                Func("YEAR", Func("FROM_UNIXTIME", Broadcast.BroadcastStart)), 
                Func("MONTH", Func("FROM_UNIXTIME", Broadcast.BroadcastStart)),
                Func("SUM", Broadcast.BroadcastEnd - Broadcast.BroadcastStart)
            ), 
            Broadcast.StationID == Station.ID,
            where
        ).group_by(Station, Func("YEAR", Func("FROM_UNIXTIME", Broadcast.BroadcastStart)), Func("MONTH", Func("FROM_UNIXTIME", Broadcast.BroadcastStart)))
        
        data = list(self._splitData(data))
        monthList = list(self._getMonthList(data))
        data = list(self._mapData(data, monthList))
        data.sort(key=lambda x: unicode(x[0]))
        
        dateList = [datetime(year, month+1, day=1, hour=0, minute=0) for year, month in monthList]
        xticks = list(self._filterTicksExt(dateList, monthList))
        tickCoords = [float(i)+0.5 for i in self._filterTicksExt(range(len(monthList)), monthList)]
        coords = [i for i in xrange(len(monthList))]
        
        return (data, coords, xticks, tickCoords)
        
    def setupAxes(self, figure, dataTuple,
        fontProp = None,
        axisColour=(0.3, 0.3, 0.3, 1.0),
        labelColour=(0., 0., 0., 1.0), 
        gridColour=(0.5, 0.5, 0.5, 1.),
        title=None,
        years=None,
        **kwargs):
        
        width = self.width if years is None else years*2
        if width > self.width:
            width = width / 2.
        if width < 5:
            width = 5
        xborder_left = self.width / width * self.xborder_left
        xborder_right = self.width / width * self.xborder_right
        
        data, coords, xticks, tickCoords = dataTuple
        
        figure.set_figheight(self.height)
        figure.set_figwidth(width)
        
        ax = figure.add_axes([xborder_left, self.yborder_bottom, 1.0-(xborder_left+xborder_right), 1.0-(self.yborder_top+self.yborder_bottom)])
        ax.set_frame_on(False)
        
        ax.minorticks_on()
        
        ax.set_xticks(tickCoords)
        ax.set_xticks([coord+0.5 for coord in coords[::2]], minor=True)
        ax.set_xticklabels([u"{0} {1:d}".format(TimeUtils.monthname[dt.month-1], dt.year) for dt in xticks], rotation="vertical", font_properties=fontProp, color=labelColour)
        ax.set_ylabel("seconds of transmission", font_properties=fontProp)
        ax.set_xlabel("month", font_properties=fontProp)
        ax.grid(True, which='both', linestyle=':', color=gridColour)
        ax.tick_params(direction="out", color=axisColour)
        
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_font_properties(fontProp)
        
        ax.set_title(title or u"transmission duration per month by station", font_properties=fontProp)
        ax.axhline(linewidth=2., color=axisColour)
        ax.axvline(linewidth=2., color=axisColour)
        
        ax.tick_params(color=axisColour)
        
        return ax
        

class PlotDataPunch(PlotDataSource):
    def getLastModified(self, stationId = None, **kwargs):
        if stationId is None or stationId == 0:
            return max(
                    self.store.find(Transmission).max(Transmission.Modified),
                    self.store.find(Broadcast).max(Broadcast.TransmissionRemoved),
                    self.store.find(Station).max(Station.BroadcastRemoved))
        else:
            return max(
                    self.store.find(Transmission, 
                        Transmission.BroadcastID == Broadcast.ID,
                        Broadcast.StationID == stationId).max(Transmission.Modified),
                    self.store.find(Broadcast, Broadcast.StationID == stationId).max(Broadcast.TransmissionRemoved),
                    self.store.get(Station, stationId).BroadcastRemoved)
    
    def select(self, **kwargs):
        return []
    
    def getData(self, *args, **kwargs):
        items = self.select(**kwargs)
        
        matrix = [[0 for i in xrange(0, self.xcount)] for i in xrange(0, self.ycount)]
        maxCount = 0
        
        for item in items:
            l = matrix[item[0]-1]
            c = l[item[1]] + 1
            if c > maxCount:
                maxCount = c
            l[item[1]] = c
        
        maxCount = float(maxCount)
        return (matrix, maxCount)
    
    def setupAxes(self, figure, 
        fontProp = None,
        axisColour=(0.3, 0.3, 0.3, 1.0),
        labelColour=(0., 0., 0., 1.0), 
        **kwargs):
        
        figure.set_figheight(self.height)
        figure.set_figwidth(self.width)
        
        tickargs = {
            "color": labelColour
        }
        if fontProp is not None:
            tickargs["font_properties"] = fontProp
        
        ax = figure.add_axes([self.xborder, self.yborder, 1.0-self.xborder, 1.0-self.yborder])
        ax.set_frame_on(False)
        ax.set_xticks(range(0,self.xcount))
        ax.set_xticklabels(self.xtickLabels, **tickargs)
        ax.set_yticks(range(0,self.ycount))
        ax.set_yticklabels(self.ytickLabels, **tickargs)
        ax.axis([-0.5, self.xcount-0.5, -0.5, self.ycount - 0.5])
        
        xmin = 0.25/float(self.xcount)
        xmax = float(self.xcount-0.25)/float(self.xcount)
        
        ymin = 0.25/float(self.ycount)
        ymax = float(self.ycount-0.25)/float(self.ycount)
        
        ax.axhline(y=-0.5, xmin=xmin, xmax=xmax, color=axisColour, linewidth=2.)
        ax.axvline(x=-0.5, ymin=ymin, ymax=ymax, color=axisColour, linewidth=2.)
        ax.tick_params(color=axisColour)
        
        return ax
        
class PlotDataWeekHourPunch(PlotDataPunch):
    xborder = 0.05
    yborder = 0.06
    
    width = 12.5
    height = 4
    
    xcount = 24
    ycount = 7
    
    xtickLabels = ["{0:02d}z".format(i) for i in xrange(0, 24)]
    ytickLabels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    
    def select(self, stationId = None, **kwargs):
        cols = (
            Func("DAYOFWEEK", Func("FROM_UNIXTIME", Transmission.Timestamp)),
            Func("HOUR", Func("FROM_UNIXTIME", Transmission.Timestamp))
        )
        data = None
        if stationId is None:
            data = self.store.find(cols)
        else:
            data = self.store.find(
                cols,
                Transmission.BroadcastID == Broadcast.ID,
                Broadcast.StationID == stationId
            )
        return data

class PlotDataMonthHourPunch(PlotDataPunch):
    xborder=0.05
    yborder=0.04
    
    width = 12.5
    height = 6
    
    xcount = 24
    ycount = 12
    
    xtickLabels = PlotDataWeekHourPunch.xtickLabels
    ytickLabels = TimeUtils.monthname
    
    def select(self, stationId = None, **kwargs):
        cols = (
            Func("MONTH", Func("FROM_UNIXTIME", Transmission.Timestamp)),
            Func("HOUR", Func("FROM_UNIXTIME", Transmission.Timestamp))
        )
        data = None
        if stationId is None:
            data = self.store.find(cols)
        else:
            data = self.store.find(
                cols,
                Transmission.BroadcastID == Broadcast.ID,
                Broadcast.StationID == stationId
            )
        return data
