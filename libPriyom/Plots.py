import numpy
import matplotlib
matplotlib.use("cairo")
import math
from matplotlib import pyplot, transforms
import matplotlib.font_manager as fonts
import matplotlib.colors as colors
import itertools
from .PlotDataSources import *
from datetime import datetime, timedelta
from .Helpers.TimeUtils import monthname

defaultColours = [
    (1.0, 0.0, 0.0, 1.0),
    (1.0, 0.5019607843137255, 0.0, 1.0),
    (1.0, 1.0, 0.0, 1.0),
    (1.0, 0.0, 0.5019607843137255, 1.0),
    (1.0, 0.0, 1.0, 1.0),
    (0.5019607843137255, 1.0, 0.0, 1.0),
    (0.0, 1.0, 0.0, 1.0),
    (0.0, 1.0, 0.5019607843137255, 1.0),
    (0.0, 1.0, 1.0, 1.0),
    (0.0, 0.5019607843137255, 1.0, 1.0),
    (0.0, 0.0, 1.0, 1.0),
    (0.5019607843137255, 0.0, 1.0, 1.0),
    (1.0, 0.5019607843137255, 0.5019607843137255, 1.0),
    (1.0, 0.7529411764705882, 0.5019607843137255, 1.0),
    (1.0, 1.0, 0.5019607843137255, 1.0),
    (1.0, 0.5019607843137255, 0.7529411764705882, 1.0),
    (1.0, 0.5019607843137255, 1.0, 1.0),
    (0.7529411764705882, 1.0, 0.5019607843137255, 1.0),
    (0.5019607843137255, 1.0, 0.5019607843137255, 1.0),
    (0.5019607843137255, 1.0, 0.7529411764705882, 1.0),
    (0.5019607843137255, 1.0, 1.0, 1.0),
    (0.5019607843137255, 0.7529411764705882, 1.0, 1.0),
    (0.5019607843137255, 0.5019607843137255, 1.0, 1.0),
    (0.7529411764705882, 0.5019607843137255, 1.0, 1.0),
    (0.5019607843137255, 0.25098039215686274, 0.25098039215686274, 1.0),
    (0.5019607843137255, 0.3764705882352941, 0.25098039215686274, 1.0),
    (0.5019607843137255, 0.5019607843137255, 0.25098039215686274, 1.0),
    (0.5019607843137255, 0.25098039215686274, 0.3764705882352941, 1.0),
    (0.5019607843137255, 0.25098039215686274, 0.5019607843137255, 1.0),
    (0.5019607843137255, 0.5019607843137255, 0.25098039215686274, 1.0),
    (0.3764705882352941, 0.5019607843137255, 0.25098039215686274, 1.0),
    (0.25098039215686274, 0.5019607843137255, 0.25098039215686274, 1.0),
    (0.25098039215686274, 0.5019607843137255, 0.3764705882352941, 1.0),
    (0.25098039215686274, 0.5019607843137255, 0.5019607843137255, 1.0),
    (0.25098039215686274, 0.3764705882352941, 0.5019607843137255, 1.0),
    (0.25098039215686274, 0.25098039215686274, 0.5019607843137255, 1.0),
    (0.3764705882352941, 0.25098039215686274, 0.5019607843137255, 1.0),
    (0., 0., 0., 1.)
]

class PlotRenderer(object):
    def raiseIncompatibleDataSource(self, dataSource):
        raise Exception(u"Data source of type {0} is not compatible to {1}.".format(unicode(type(dataSource)), unicode(self)))
        
    def checkDataSource(self, dataSource):
        pass
    
    def plotGraph(self, dataSource, outFileName, dpi=72, format="png", transparent=True, **kwargs):
        self.checkDataSource(dataSource)
        
        figure = self._plotGraph(dataSource, **kwargs)
        figure.savefig(outFileName, dpi=dpi, format=format, transparent=transparent)
        pyplot.close(figure)
        del figure


class PlotPunchCard(PlotRenderer):
    def checkDataSource(self, dataSource):
        if not isinstance(dataSource, PlotDataPunch):
            self.raiseIncompatibleDataSource(dataSource)
        
    def _doPlot(self, figure, ax, fontProp, 
            scale=200.,
            blobColour=(0., 0., 0., 1.0),
            **kwargs):
        
        xcount = len(self.matrix[0])
        ycount = len(self.matrix)
        
        coords = list(itertools.product(range(0,ycount), range(0,xcount)))
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
            
    def interpolateMatrixMirrored(self, subdivision, matrix, mirrorMode):
        xcount = len(matrix)
        if xcount == 0:
            yield None
            return
        ycount = len(matrix[0])
        if ycount == 0:
            yield None
            return
        
        mirrorMode = 0.5 if mirrorMode == 2 else 1.0
        
        for x in xrange(int(-0.5*subdivision),int((xcount-mirrorMode)*subdivision+1)):
            oldx = float(x)/float(subdivision)
            x0 = int(math.floor(oldx))
            x1 = x0+1
            if x0 < 0:
                x0 = x0 + xcount
            elif x0 >= xcount:
                x0 = x0 - xcount
            if x1 < 0:
                x1 = x1 + xcount
            elif x1 >= xcount:
                x1 = x1 - xcount
            items = list(xrange(int(-0.5*subdivision), int((ycount-mirrorMode)*subdivision+1)))
            for idx, y in itertools.izip(xrange(len(items)), items):
                oldy = float(y)/float(subdivision)
                y0 = int(math.floor(oldy))
                y1 = y0 + 1
                if y0 < 0:
                    y0 = y0 + ycount
                elif y0 >= ycount:
                    y0 = y0 - ycount
                if y1 < 0:
                    y1 = y1 + ycount
                elif y1 >= ycount:
                    y1 = y1 - ycount
                items[idx] = self.interpolate(
                    matrix[x0][y0],
                    matrix[x1][y0],
                    matrix[x0][y1],
                    matrix[x1][y1],
                    oldx-int(math.floor(oldx)),
                    oldy-int(math.floor(oldy))
                )
            yield items
    
    def _doPlot(self, figure, ax, fontProp,
            gridColour=(0.6, 0.6, 0.6, 1.0),
            subdivision=1,
            levels=23,
            mirrored=False,
            **kwargs):
        
        xcount = len(self.matrix[0])
        ycount = len(self.matrix)
        
        if subdivision > 1:
            if mirrored:
                mirrorMode = 1 if mirrored == True or mirrored == 1 else 2
                newdata = list(self.interpolateMatrixMirrored(subdivision, self.matrix, mirrorMode))
            else:
                newdata = list(self.interpolateMatrix(subdivision, self.matrix))
        else:
            newdata = self.matrix
        if not mirrored:
            xlist = [float(i)/float(subdivision) for i in xrange(0,(xcount-1)*subdivision+1)]
            ylist = [float(i)/float(subdivision) for i in xrange(0,(ycount-1)*subdivision+1)]
        else:
            xlist = [float(i)/float(subdivision) for i in xrange(int(-0.5*subdivision),int((xcount-1./float(mirrorMode))*subdivision+1))]
            ylist = [float(i)/float(subdivision) for i in xrange(int(-0.5*subdivision),int((ycount-1./float(mirrorMode))*subdivision+1))]
        
        normalizer = colors.Normalize(0., self.maxCount)
        cs = ax.contourf(xlist, ylist, newdata, levels, norm=normalizer)
        ax.contour(xlist, ylist, newdata, levels, norm=normalizer)
        cbar = figure.colorbar(cs, ax=ax, shrink=0.8, pad=(0. if not mirrored or mirrorMode == 1 else 0.01), fraction=0.06)
        for tick in cbar.ax.xaxis.get_major_ticks() + cbar.ax.yaxis.get_major_ticks():
            tick.label1.set_font_properties(fontProp)
            tick.label2.set_font_properties(fontProp)
        
        ax.grid(True, color=gridColour)

class PlotStackedGraph(PlotRenderer):
    def checkDataSource(self, dataSource):
        if not isinstance(dataSource, PlotDataUptime):
            self.raiseIncompatibleDataSource(dataSource)
            
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
                for year in xrange(prevMonth[0], t[0]):
                    minMonth = 0 if year > prevMonth[0] else prevMonth[1]+1
                    if minMonth == 12:
                        continue
                    maxMonth = 12 if year < t[0]-1 else t[1]-1
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
            
    def _filterTicks(self, monthList):
        yield monthList[0]
        for item in monthList[1:-1]:
            month = item[1]
            if not month in (0, 3, 6, 9):
                continue
            yield item
        yield monthList[-1]
            
    def _filterTicksExt(self, list, reference):
        yield list[0]
        for item, ref in itertools.izip(list[1:-1], reference[1:-1]):
            month = ref[1]
            if not month in (0, 3, 6, 9):
                continue
            yield item
        yield list[-1]
    
    def _plotGraph(self, dataSource, fontFamily="sans", fontSize=10, **kwargs):
        global defaultColours
        fontProp = fonts.FontProperties(fontFamily, size=fontSize)
        
        self.data = list(self._splitData(dataSource.getData(**kwargs)))
        monthList = list(self._getMonthList(self.data))
        self.data = list(self._mapData(self.data, monthList))
        
        #minMonth = self.data[0][1][0]
        #minMonth = float(minMonth[0])*12.+float(minMonth[1])
        #minYear = int(minMonth)
        xticks = [datetime(year, month+1, day=1, hour=0, minute=0) for year, month in self._filterTicks(monthList)]
        tickCoords = [float(i)+0.5 for i in self._filterTicksExt(range(len(monthList)), monthList)]
        coords = [i for i in xrange(len(monthList))]
        
        
        figure = pyplot.figure()
        ax = dataSource.setupAxes(figure, fontProp=fontProp, **kwargs)
        stationPlots = list()
        bottom = [0 for i in xrange(len(coords))]
        i = 0
        for station, data in self.data:
            durations = [duration for year, month, duration in data]
            plot = ax.bar(coords, durations, 1.0, color=defaultColours[i], bottom=bottom)
            stationPlots.append(plot[0])
            bottom = [prevBottom+currHeight for prevBottom, currHeight in itertools.izip(bottom, durations)]
            i += 1
            if i >= len(defaultColours):
                i = len(defaultColours)-1
        
        ax.minorticks_on()
        ax.set_xticks(tickCoords)
        ax.set_xticks([], minor=True)
        ax.set_xticklabels([u"{0} {1:d}".format(monthname[dt.month-1], dt.year) for dt in xticks], rotation="vertical", font_properties=fontProp)
        ax.set_ylabel("seconds of transmission", font_properties=fontProp)
        ax.set_xlabel("month", font_properties=fontProp)
        ax.set_title("Transmission duration per month by station", font_properties=fontProp)
        ax.grid(True)
        ax.legend(stationPlots, [unicode(station) for station, data in self.data], loc='upper left', prop=fontProp)
        
        return figure
        
