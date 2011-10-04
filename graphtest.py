#!/usr/bin/python2
from priyomdbtest import *
from storm.expr import *
import itertools
data = store.find(
    (
        Func("DAYOFWEEK", Func("FROM_UNIXTIME", Transmission.Timestamp)), 
        Func("HOUR", Func("FROM_UNIXTIME", Transmission.Timestamp))
    ))

matrix = [[0 for i in xrange(0,24)] for i in xrange(0,7)]

maxCount = 0
for item in data:
    l = matrix[item[0]-1]
    c = l[item[1]] + 1
    if c > maxCount:
        maxCount = c
    l[item[1]] = c
maxCount = float(maxCount)
scale = 100.

coords = list(itertools.product(range(0,7), range(0,24)))
xlist = [item[1] for item in coords]
ylist = [item[0] for item in coords]

size = [float(matrix[x][y])/maxCount * scale for x,y in coords]
print(x)
print(y)
print(size)

import matplotlib
matplotlib.use('cairo')
matplotlib.rcParams['text.hinting'] = True
import matplotlib.pyplot as plt
import matplotlib.transforms as trans
import matplotlib.ft2font as ft2
import matplotlib.font_manager as fonts

blobcolor = (0., 0., 0., 1.0)
axiscolor = (0.3, 0.3, 0.3, 1.0)
labelcolor = (0., 0., 0., 1.0)
xborder = 0.05
yborder = 0.06

#font = ft2.FT2Font("/home/horazont/Projects/fpc/sg/fpc-edition/mods/.default/ffx/dejavu_sans_b.ttf")#fonts.FontProperties(family="sans", size=8.)
fontprop = fonts.FontProperties("sans", size=10)
#font.set_fontconfig_pattern("sans-8:hinting=true")

fig = plt.figure(figsize=(12.5, 4))
ax = fig.add_axes([xborder, yborder, 1.0-xborder, 1.0-yborder])
#ax = fig.add_axes([0, 0, 1, 1])
plt.box(False)
plt.xticks(range(0,24), ["{0:02d}z".format(i) for i in xrange(0, 24)], color=labelcolor, font_properties=fontprop)
plt.yticks(range(0,7), ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], color=labelcolor, font_properties=fontprop)
plt.axis([-0.5, 23.5, -0.5, 6.5])
plt.scatter(x=xlist, y=ylist, s=size, color=[blobcolor])
plt.axhline(y=-0.5, xmin=0.25/24, xmax=23.75/24, color=axiscolor, linewidth=2.)
plt.axvline(x=-0.5, ymin=0.25/7, ymax=6.75/7, color=axiscolor, linewidth=2.)
plt.minorticks_off()
plt.tick_params(direction="out", top="off", right="off", color=axiscolor)
for tick in ax.xaxis.get_major_ticks() + ax.yaxis.get_major_ticks():
    tick.tick1line.set_markeredgewidth(1.)
    tick.tick1line.set_markersize(5.)
plt.savefig("/tmp/test.png", dpi=72, format="png", transparent=True)
# plt.show()
