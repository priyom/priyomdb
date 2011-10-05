from storm.locals import *
from storm.expr import *
import numpy
import matplotlib
matplotlib.use("cairo")
import math
from matplotlib import pyplot, transforms
import matplotlib.font_manager as fonts
import itertools
from Transmission import Transmission
from Broadcast import Broadcast
        
class PlotDataSource(object):
    def __init__(self, store):
        self.store = store
        
    def getData(self, *args, **kwargs):
        pass
    
    def setupAxis(self, figure, ax, **kwargs):
        pass

class PlotRenderer(object):
    def raiseIncompatibleDataSource(self, dataSource):
        raise Exception(u"Data source of type {0} is not compatible to {1}.".format(unicode(type(dataSource)), unicode(self)))
    
    def plotGraph(self, dataSource, outFileName, dpi=72, format="png", transparent=True, **kwargs):
        if not type(dataSource) in [PlotDataWeekHourPunch]:
            self.raiseIncompatibleDataSource(dataSource)
        
        figure = self._plotGraph(dataSource, **kwargs)
        figure.savefig(outFileName, dpi=dpi, format=format, transparent=transparent)
        pyplot.close(figure)
        del figure
        
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
        
class PlotDataWeekHourPunch(PlotDataPunch):
    xborder = 0.05
    yborder = 0.06
    
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
    
    def setupAxes(self, figure, 
        fontProp = None,
        axisColour=(0.3, 0.3, 0.3, 1.0),
        labelColour=(0., 0., 0., 1.0)):
        
        figure.set_figheight(4)
        figure.set_figwidth(12.5)
        
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
        

class PlotPunchCard(PlotRenderer):
        
    def _doPlot(self, figure, ax, fontProp, 
            scale=200.,
            blobColour=(0., 0., 0., 1.0)):
        coords = list(itertools.product(range(0,7), range(0,24)))
        xlist = [item[1] for item in coords]
        ylist = [item[0] for item in coords]
        matrix = self.matrix
        maxCount = self.maxCount
        
        size = [(float(matrix[x][y])/maxCount) * scale for x,y in coords]
        
        ax.scatter(x=xlist, y=ylist, s=size, color=blobColour)
        
    def _plotGraph(self, 
            dataSource,
            fontFamily="sans",
            fontSize=10.,
            **kwargs):
                
        fontProp = fonts.FontProperties(fontFamily, size=fontSize)
        
        self.matrix, self.maxCount = dataSource.getData(**kwargs)
        
        figure = pyplot.figure()
        ax = dataSource.setupAxes(figure, fontProp=fontProp, **kwargs)
        self._doPlot(figure, ax, fontProp, **kwargs)
        ax.minorticks_off()
        ax.tick_params(direction="out", top="off", right="off")
        
        for tick in ax.xaxis.get_major_ticks() + ax.yaxis.get_major_ticks():
            tick.tick1line.set_markeredgewidth(1.)
            tick.tick1line.set_markersize(5.)
        
        return figure

class PlotColourCard(PlotPunchCard):
    def interpolateOne(self, v0, v1, vfac):
        fc = math.cos(vfac * math.pi * 0.5)
        fc = fc * fc
        return fc * v0 + (1.0 - fc) * v1

    def interpolate(self, v00, v01, v10, v11, xfac, yfac):
        v0 = self.interpolateOne(v00, v01, xfac)
        v1 = self.interpolateOne(v10, v11, xfac)
        
        return self.interpolateOne(v0, v1, yfac)
        
    def interpolateMatrix(self, subdivision, matrix):
        xcount = len(matrix)
        if xcount == 0:
            yield None
            return
        ycount = len(matrix[0])
        if ycount == 0:
            yield None
            return
        for x in xrange((xcount-1)*subdivision+1):
            oldx = float(x)/float(subdivision)
            x0 = int(math.floor(oldx))
            x1 = x0+1
            if x1 >= xcount:
                x1 = x0
            items = list(xrange((ycount-1)*subdivision+1))
            for y in xrange(len(items)):
                oldy = float(y)/float(subdivision)
                y0 = int(math.floor(oldy))
                y1 = y0+1
                if y1 >= ycount:
                    y1 = y0
                items[y] = self.interpolate(
                    matrix[x0][y0],
                    matrix[x1][y0],
                    matrix[x0][y1],
                    matrix[x1][y1],
                    oldx-x0,
                    oldy-y0
                )
            yield items
    
    def _doPlot(self, figure, ax, fontProp,
            gridColour=(0.6, 0.6, 0.6, 1.0),
            subdivision=1,
            levels=23):
        
        xlist = [float(i)/float(subdivision) for i in xrange(0,23*subdivision+1)]
        ylist = [float(i)/float(subdivision) for i in xrange(0,6*subdivision+1)]
        if subdivision > 1:
            newdata = list(self.interpolateMatrix(subdivision, self.matrix))
        else:
            newdata = self.matrix
        
        cs = ax.contourf(xlist, ylist, newdata, levels)
        cbar = figure.colorbar(cs, ax=ax, shrink=0.8, pad=0., fraction=0.05)
        for tick in cbar.ax.xaxis.get_major_ticks() + cbar.ax.yaxis.get_major_ticks():
            tick.label1.set_font_properties(fontProp)
            tick.label2.set_font_properties(fontProp)
        
        ax.grid(True, color=gridColour)


