import numpy
import matplotlib
matplotlib.use("cairo")
import math
from matplotlib import pyplot, transforms
import matplotlib.font_manager as fonts
import itertools
from .PlotDataSources import *

class PlotRenderer(object):
    def raiseIncompatibleDataSource(self, dataSource):
        raise Exception(u"Data source of type {0} is not compatible to {1}.".format(unicode(type(dataSource)), unicode(self)))
    
    def plotGraph(self, dataSource, outFileName, dpi=72, format="png", transparent=True, **kwargs):
        if not isinstance(dataSource, PlotDataPunch):
            self.raiseIncompatibleDataSource(dataSource)
        
        figure = self._plotGraph(dataSource, **kwargs)
        figure.savefig(outFileName, dpi=dpi, format=format, transparent=transparent)
        pyplot.close(figure)
        del figure


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


