#!/usr/bin/python2
"""
File name: graphtest.py
This file is part of: priyomdb

LICENSE

The contents of this file are subject to the Mozilla Public License
Version 1.1 (the "License"); you may not use this file except in
compliance with the License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/

Software distributed under the License is distributed on an "AS IS"
basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
License for the specific language governing rights and limitations under
the License.

Alternatively, the contents of this file may be used under the terms of
the GNU General Public license (the  "GPL License"), in which case  the
provisions of GPL License are applicable instead of those above.

FEEDBACK & QUESTIONS

For feedback and questions about priyomdb please e-mail one of the
authors:
    Jonas Wielicki <j.wielicki@sotecware.net>
"""
from priyomdbtest import *
from storm.expr import *
import itertools
data = store.find(
    (
        Func("DAYOFWEEK", Func("FROM_UNIXTIME", Transmission.Timestamp)), 
        Func("HOUR", Func("FROM_UNIXTIME", Transmission.Timestamp))
    ), 
    Transmission.BroadcastID == Broadcast.ID,
    Broadcast.StationID == 1)

matrix = [[0 for i in xrange(0,24)] for i in xrange(0,7)]

maxCount = 0
for item in data:
    l = matrix[item[0]-1]
    c = l[item[1]] + 1
    if c > maxCount:
        maxCount = c
    l[item[1]] = c
maxCount = float(maxCount)
scale = 200.

coords = list(itertools.product(range(0,7), range(0,24)))
xlist = [item[1] for item in coords]
ylist = [item[0] for item in coords]

normalized = [float(matrix[x][y])/maxCount for x,y in coords]
size = [v * scale for v in normalized]

import matplotlib
matplotlib.use('cairo')
matplotlib.rcParams['text.hinting'] = True
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as trans
import matplotlib.ft2font as ft2
import matplotlib.font_manager as fonts
import math

blobcolor = (0., 0., 0., 1.0)
axiscolor = (0.3, 0.3, 0.3, 1.0)
gridcolor = (0.6, 0.6, 0.6, 1.0)
labelcolor = (0., 0., 0., 1.0)
xborder0 = 0.05
xborder1 = 0.0
yborder = 0.06
subdivision = 10

xlistfine = [float(i)/float(subdivision) for i in xrange(0,23*subdivision+1)]
ylistfine = [float(i)/float(subdivision) for i in xrange(0,6*subdivision+1)]


def interpolateOne(v0, v1, vfac):
    fc = math.cos(vfac * math.pi * 0.5)
    fc = fc * fc
    return fc * v0 + (1.0 - fc) * v1

def interpolate(v00, v01, v10, v11, xfac, yfac):
    v0 = interpolateOne(v00, v01, xfac)
    v1 = interpolateOne(v10, v11, xfac)
    
    return interpolateOne(v0, v1, yfac)
    
def interpolateMatrix(subdivision, matrix):
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
            items[y] = interpolate(
                matrix[x0][y0],
                matrix[x1][y0],
                matrix[x0][y1],
                matrix[x1][y1],
                oldx-x0,
                oldy-y0
            )
        yield items

newdata = list(interpolateMatrix(subdivision, matrix))

#font = ft2.FT2Font("/home/horazont/Projects/fpc/sg/fpc-edition/mods/.default/ffx/dejavu_sans_b.ttf")#fonts.FontProperties(family="sans", size=8.)
fontprop = fonts.FontProperties("sans", size=10)
#font.set_fontconfig_pattern("sans-8:hinting=true")

print("setup")
fig = plt.figure(figsize=(12.5, 4))
ax = fig.add_axes([xborder0, yborder, 1.0-(xborder0+xborder1), 1.0-yborder])
#ax = fig.add_axes([0, 0, 1, 1])
plt.box(False)
plt.xticks(range(0,24), ["{0:02d}z".format(i) for i in xrange(0, 24)], color=labelcolor, font_properties=fontprop)
plt.yticks(range(0,7), ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], color=labelcolor, font_properties=fontprop)
plt.axis([-0.5, 23.5, -0.5, 6.5])
#plt.scatter(x=xlist, y=ylist, s=size, color=[blobcolor])
cs = plt.contourf(xlistfine, ylistfine, newdata, 123)
cbar = plt.colorbar(cs, ax=ax, shrink=0.8, pad=0., fraction=0.05)
for tick in cbar.ax.xaxis.get_major_ticks() + cbar.ax.yaxis.get_major_ticks():
    tick.label1.set_font_properties(fontprop)
    tick.label2.set_font_properties(fontprop)
plt.axhline(y=-0.5, xmin=0.25/24, xmax=23.75/24, color=axiscolor, linewidth=2.)
plt.axvline(x=-0.5, ymin=0.25/7, ymax=6.75/7, color=axiscolor, linewidth=2.)
ax.grid(True, color=gridcolor)#, clip_on=True, clip_box=trans.Bbox.from_bounds(0, 0, 24*4*subdivision, 7*4*subdivision), color=gridcolor)
plt.minorticks_off()
plt.tick_params(direction="out", top="off", right="off", color=axiscolor)
for tick in ax.xaxis.get_major_ticks() + ax.yaxis.get_major_ticks():
    tick.tick1line.set_markeredgewidth(1.)
    tick.tick1line.set_markersize(5.)
print("rendering")
plt.savefig("/tmp/test.png", dpi=300, format="png", transparent=True)
print("finished")
# plt.show()
