from storm.locals import *
from storm.expr import *
from Transmission import Transmission
from Broadcast import Broadcast

__all__ = ['PlotDataSource', 'PlotDataPunch', 'PlotDataWeekHourPunch', 'PlotDataMonthHourPunch']

class PlotDataSource(object):
    def __init__(self, store):
        self.store = store
        
    def getData(self, *args, **kwargs):
        pass
    
    def setupAxis(self, figure, ax, **kwargs):
        pass

class PlotDataPunch(PlotDataSource):
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
    ytickLabels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Oct", "Sep", "Nov", "Dec"]
    
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
