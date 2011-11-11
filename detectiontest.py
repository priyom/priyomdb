#!/usr/bin/python2
from datetime import datetime, timedelta
import numpy
import itertools
import math
import random
import numpy.dual
import matplotlib
#matplotlib.use('cairo')
#matplotlib.rcParams['text.hinting'] = True
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as trans
import matplotlib.ft2font as ft2
import matplotlib.font_manager as fonts
import math
import scipy.signal as signal

startAt = datetime(2010, 01, 01)
clipAt = datetime(2012, 01, 01)

def txes(startYear, startMonth, startDay, hour, minute, count, daysOffset, noise=True):
    zero = datetime(startYear, startMonth, startDay, hour, minute)
    yield zero
    secondsOffset = [0]
    for i in xrange(count-1):
        if noise:
            secondsOffset = numpy.random.normal(0., 15., 1) * 60.0
        yield (zero + timedelta(days=daysOffset*(i+1), seconds=secondsOffset[0]))
        

data = []
data += list(txes(2011, 01, 03, 2, 00, 52, 7, True))
data += list(txes(2011, 01, 01, 16, 00, 500, 1, True))
#data += list(txes(2011, 01, 02, 16, 00, 31, 1))
#data.append(datetime(2011, 01, 01))
#data = [datetime(2011, 2, 6, 2, 1, 30), datetime(2011, 2, 12, 1, 30), datetime(2011, 2, 20, 1, 30), datetime(2011, 2, 26, 1, 30), datetime(2011, 3, 5, 1, 30), datetime(2011, 3, 6, 1, 30), datetime(2011, 3, 12, 1, 30), datetime(2011, 3, 17, 20, 30), datetime(2011, 3, 20, 1, 30), datetime(2011, 3, 26, 1, 30), datetime(2011, 4, 3, 0, 30), datetime(2011, 4, 9, 1, 30), datetime(2011, 4, 21, 20, 30), datetime(2011, 4, 22, 21, 30), datetime(2011, 4, 30, 0, 30), datetime(2011, 5, 6, 21, 30), datetime(2011, 5, 8, 0, 30), datetime(2011, 5, 13, 0, 30), datetime(2011, 5, 20, 21, 30), datetime(2011, 5, 21, 0, 30), datetime(2011, 5, 26, 6, 0), datetime(2011, 5, 28, 1, 30), datetime(2011, 6, 3, 21, 30), datetime(2011, 6, 4, 0, 30), datetime(2011, 6, 12, 0, 30), datetime(2011, 6, 16, 20, 30), datetime(2011, 6, 17, 21, 30), datetime(2011, 6, 18, 0, 30), datetime(2011, 6, 24, 14, 0), datetime(2011, 6, 25, 0, 30), datetime(2011, 7, 3, 0, 30), datetime(2011, 7, 9, 0, 30), datetime(2011, 7, 17, 14, 20, 26), datetime(2011, 8, 5, 21, 30), datetime(2011, 8, 13, 1, 30), datetime(2011, 8, 18, 6, 0), datetime(2011, 8, 28, 0, 30), datetime(2011, 9, 11, 0, 30), datetime(2011, 9, 15, 20, 40), datetime(2011, 10, 6, 20, 30), datetime(2011, 10, 9, 1, 30), datetime(2011, 10, 20, 20, 30), datetime(2011, 10, 22, 0, 30), datetime(2011, 3, 17, 19, 30), datetime(2011, 11, 4, 21, 30)]

#buzzer = [datetime(1997, 12, 24, 23, 0), datetime(2010, 9, 10, 17, 16), datetime(2010, 9, 5, 15, 39), datetime(2010, 8, 25, 8, 54), datetime(2010, 8, 23, 15, 35), datetime(2010, 1, 25, 19, 13), datetime(2010, 9, 7, 18, 48), datetime(2010, 9, 8, 10, 12), datetime(2010, 9, 8, 18, 4), datetime(2010, 9, 8, 18, 18), datetime(2010, 9, 11, 9, 20), datetime(2010, 9, 11, 13, 30), datetime(2010, 9, 12, 15, 4), datetime(2010, 9, 13, 17, 14), datetime(2010, 9, 14, 9, 17), datetime(2010, 9, 14, 12, 51), datetime(2010, 9, 16, 18, 39), datetime(2010, 9, 17, 13, 52), datetime(2010, 9, 17, 14, 26), datetime(2010, 9, 18, 18, 30), datetime(2010, 9, 19, 16, 44), datetime(2010, 9, 22, 9, 0), datetime(2010, 9, 27, 15, 3), datetime(2010, 9, 29, 8, 35), datetime(2010, 9, 30, 13, 14), datetime(2010, 9, 30, 13, 48), datetime(2010, 9, 30, 14, 30), datetime(2010, 9, 30, 14, 37), datetime(2010, 9, 30, 14, 52), datetime(2010, 9, 30, 14, 58), datetime(2010, 9, 30, 15, 2), datetime(2010, 10, 2, 14, 55), datetime(2010, 10, 3, 15, 47), datetime(2010, 10, 4, 10, 26), datetime(2010, 10, 4, 11, 13), datetime(2010, 10, 5, 15, 26), datetime(2010, 10, 6, 15, 24), datetime(2010, 10, 7, 16, 34), datetime(2010, 10, 7, 16, 53), datetime(2010, 10, 8, 15, 41), datetime(2010, 10, 12, 15, 36), datetime(2010, 10, 14, 15, 13), datetime(2010, 10, 14, 15, 15), datetime(2010, 10, 14, 15, 17), datetime(2010, 10, 14, 15, 33), datetime(2010, 10, 16, 17, 5), datetime(2010, 10, 17, 16, 23), datetime(2010, 10, 17, 16, 42), datetime(2010, 10, 19, 16, 2), datetime(2010, 10, 20, 15, 27), datetime(2010, 10, 21, 14, 12), datetime(2010, 10, 21, 14, 48), datetime(2010, 10, 25, 15, 20), datetime(2010, 10, 27, 16, 1), datetime(2010, 10, 28, 12, 43), datetime(2010, 10, 28, 17, 15), datetime(2010, 10, 29, 16, 4), datetime(2010, 10, 30, 16, 11), datetime(2010, 10, 31, 16, 14), datetime(2010, 10, 31, 17, 0), datetime(2010, 11, 1, 18, 3), datetime(2010, 11, 4, 16, 50), datetime(2010, 11, 6, 17, 0), datetime(2010, 11, 7, 16, 37), datetime(2010, 11, 7, 16, 39), datetime(2010, 11, 8, 19, 2), datetime(2010, 11, 10, 14, 57), datetime(2010, 11, 10, 15, 20), datetime(2010, 11, 12, 18, 33), datetime(2010, 11, 15, 16, 36), datetime(2010, 11, 18, 15, 54), datetime(2010, 11, 20, 19, 16), datetime(2010, 11, 21, 17, 0), datetime(2010, 11, 22, 16, 43), datetime(2010, 11, 23, 15, 45), datetime(2010, 11, 24, 11, 0), datetime(2010, 11, 25, 18, 15), datetime(2010, 11, 26, 17, 19), datetime(2010, 11, 27, 16, 40), datetime(2010, 11, 29, 16, 5), datetime(2010, 11, 29, 16, 43), datetime(2010, 11, 30, 17, 3), datetime(2010, 12, 1, 16, 22), datetime(2010, 12, 2, 16, 40), datetime(2010, 12, 3, 17, 16), datetime(2010, 12, 5, 14, 22), datetime(2010, 12, 5, 16, 40), datetime(2010, 12, 6, 13, 30), datetime(2010, 12, 6, 16, 40), datetime(2010, 12, 6, 17, 8), datetime(2010, 12, 7, 12, 20), datetime(2010, 12, 8, 17, 35), datetime(2010, 12, 9, 13, 43), datetime(2010, 12, 9, 14, 6), datetime(2010, 12, 9, 14, 33), datetime(2010, 12, 9, 16, 2), datetime(2010, 12, 9, 16, 34), datetime(2010, 12, 10, 13, 45), datetime(2010, 12, 12, 16, 25), datetime(2010, 12, 13, 13, 13), datetime(2010, 12, 14, 8, 26), datetime(2010, 12, 14, 17, 6), datetime(2010, 12, 16, 15, 43), datetime(2010, 12, 18, 16, 10), datetime(2010, 12, 19, 13, 40), datetime(2010, 12, 21, 16, 40), datetime(2010, 12, 22, 14, 57), datetime(2010, 12, 24, 17, 25), datetime(2010, 12, 25, 14, 30), datetime(2010, 12, 26, 16, 55), datetime(2010, 12, 27, 9, 29), datetime(2010, 12, 27, 10, 26), datetime(2010, 12, 28, 15, 50), datetime(2010, 12, 29, 18, 30), datetime(2010, 12, 30, 16, 12), datetime(2000, 12, 24, 11, 30), datetime(2002, 12, 1, 9, 51), datetime(2002, 12, 9, 6, 18), datetime(2002, 12, 20, 17, 43), datetime(2003, 1, 15, 6, 55), datetime(2003, 1, 15, 14, 30), datetime(2003, 1, 16, 16, 0), datetime(2003, 1, 16, 16, 56), datetime(2003, 1, 17, 8, 0), datetime(2003, 1, 17, 13, 2), datetime(2003, 1, 21, 8, 52), datetime(2003, 1, 24, 16, 25), datetime(2003, 1, 30, 7, 4), datetime(2003, 1, 30, 16, 57), datetime(2003, 2, 7, 8, 34), datetime(2003, 2, 11, 16, 58), datetime(2003, 3, 1, 9, 30), datetime(2003, 3, 21, 8, 28), datetime(2003, 3, 24, 5, 51), datetime(2009, 9, 29, 18, 0), datetime(2011, 1, 5, 15, 2), datetime(2011, 1, 5, 15, 3), datetime(2011, 1, 11, 10, 38), datetime(2011, 1, 14, 15, 52), datetime(2011, 1, 17, 16, 11), datetime(2011, 1, 19, 3, 15), datetime(2011, 1, 20, 3, 2), datetime(2011, 1, 21, 7, 57), datetime(2011, 1, 26, 15, 58), datetime(2011, 1, 28, 16, 8), datetime(2011, 1, 28, 16, 36), datetime(2011, 1, 30, 15, 22), datetime(2011, 1, 31, 16, 54), datetime(2011, 2, 1, 14, 47), datetime(2011, 2, 2, 14, 47), datetime(2011, 2, 3, 15, 28), datetime(2011, 2, 4, 16, 3), datetime(2011, 2, 5, 12, 36), datetime(2011, 2, 5, 12, 50), datetime(2011, 2, 6, 15, 45), datetime(2011, 2, 7, 13, 40), datetime(2011, 2, 7, 14, 30), datetime(2011, 2, 7, 14, 44), datetime(2011, 2, 7, 16, 26), datetime(2011, 2, 8, 16, 9), datetime(2011, 2, 10, 15, 20), datetime(2011, 2, 10, 15, 22), datetime(2011, 2, 11, 15, 26), datetime(2011, 2, 13, 16, 15), datetime(2011, 2, 14, 15, 48), datetime(2011, 2, 15, 17, 35), datetime(2011, 2, 15, 17, 37), datetime(2011, 2, 18, 15, 51), datetime(2011, 2, 21, 10, 16), datetime(2011, 2, 21, 12, 47), datetime(2011, 2, 21, 13, 33), datetime(2011, 2, 21, 15, 1), datetime(2011, 2, 21, 15, 19), datetime(2011, 2, 21, 15, 58), datetime(2011, 2, 22, 10, 40), datetime(2011, 2, 24, 11, 8), datetime(2011, 2, 24, 11, 12), datetime(2011, 2, 24, 11, 58), datetime(2011, 2, 24, 12, 1), datetime(2011, 2, 24, 12, 18), datetime(2011, 2, 24, 12, 31), datetime(2011, 2, 24, 12, 39), datetime(2011, 2, 24, 13, 7), datetime(2011, 2, 24, 13, 13), datetime(2011, 2, 24, 13, 33), datetime(2011, 2, 24, 13, 55), datetime(2011, 2, 24, 14, 17), datetime(2011, 2, 24, 15, 5), datetime(2011, 2, 24, 15, 46), datetime(2011, 2, 24, 16, 23), datetime(2011, 2, 24, 16, 33), datetime(2011, 3, 5, 13, 33), datetime(2011, 3, 6, 15, 0), datetime(2011, 3, 9, 16, 30), datetime(2011, 3, 10, 11, 20), datetime(2011, 3, 11, 16, 5), datetime(2011, 3, 13, 14, 49), datetime(2011, 3, 15, 16, 30), datetime(2011, 3, 16, 17, 30), datetime(2011, 3, 16, 18, 30), datetime(2011, 3, 18, 15, 50), datetime(2011, 3, 21, 8, 0), datetime(2011, 3, 22, 6, 0), datetime(2011, 3, 22, 15, 50), datetime(2011, 3, 23, 6, 0), datetime(2011, 3, 23, 18, 5), datetime(2011, 3, 24, 15, 25), datetime(2011, 3, 25, 6, 35), datetime(2011, 3, 25, 16, 35), datetime(2011, 3, 30, 14, 10), datetime(2011, 4, 3, 15, 20), datetime(2011, 4, 4, 6, 0), datetime(2011, 4, 4, 7, 4), datetime(2011, 4, 4, 7, 41), datetime(2011, 4, 4, 14, 20), datetime(2011, 4, 7, 10, 12), datetime(2011, 4, 7, 10, 14), datetime(2011, 4, 7, 10, 50), datetime(2011, 4, 7, 11, 13), datetime(2011, 4, 7, 11, 13), datetime(2011, 4, 7, 11, 53), datetime(2011, 4, 7, 12, 5), datetime(2011, 4, 7, 12, 17), datetime(2011, 4, 7, 13, 19), datetime(2011, 4, 7, 13, 30), datetime(2011, 4, 7, 13, 45), datetime(2011, 4, 7, 12, 50), datetime(2011, 4, 10, 11, 30), datetime(2011, 4, 10, 11, 32), datetime(2011, 4, 10, 13, 5), datetime(2011, 4, 11, 13, 26), datetime(2011, 4, 13, 14, 0), datetime(2011, 4, 15, 14, 33), datetime(2011, 4, 19, 13, 37), datetime(2011, 4, 21, 9, 23), datetime(2011, 4, 21, 11, 45), datetime(2011, 4, 21, 12, 40), datetime(2011, 4, 21, 12, 45), datetime(2011, 4, 21, 12, 55), datetime(2011, 4, 21, 13, 8), datetime(2011, 4, 21, 14, 20), datetime(2011, 4, 22, 13, 15), datetime(2011, 4, 26, 14, 0), datetime(2011, 4, 27, 12, 30), datetime(2011, 4, 27, 12, 45), datetime(2011, 4, 27, 13, 30), datetime(2011, 4, 29, 9, 42), datetime(2011, 5, 5, 0, 0), datetime(2011, 5, 11, 13, 0), datetime(2011, 5, 11, 13, 5), datetime(2011, 5, 11, 14, 5), datetime(2011, 5, 12, 0, 0), datetime(2011, 5, 12, 13, 25), datetime(2011, 5, 13, 13, 50), datetime(2011, 5, 17, 13, 30), datetime(2011, 5, 19, 14, 50), datetime(2011, 5, 31, 14, 52), datetime(2011, 6, 7, 8, 0), datetime(2011, 6, 8, 12, 1), datetime(2011, 6, 15, 14, 10), datetime(2011, 7, 7, 9, 15), datetime(2011, 7, 7, 11, 45), datetime(2011, 7, 7, 13, 10), datetime(2011, 7, 7, 13, 40), datetime(2011, 7, 7, 13, 55), datetime(2011, 7, 12, 10, 40), datetime(2011, 7, 20, 14, 55), datetime(2011, 7, 20, 16, 15), datetime(2011, 7, 25, 8, 12), datetime(2011, 7, 25, 8, 22), datetime(2011, 7, 25, 9, 5), datetime(2011, 7, 25, 12, 5), datetime(2011, 7, 25, 12, 45), datetime(2011, 7, 25, 13, 20), datetime(2011, 7, 25, 13, 35), datetime(2011, 7, 28, 8, 30), datetime(2011, 7, 28, 8, 35), datetime(2011, 7, 28, 9, 10), datetime(2011, 7, 28, 9, 12), datetime(2011, 8, 18, 8, 10), datetime(2011, 8, 18, 8, 35), datetime(2011, 8, 18, 8, 35), datetime(2011, 8, 18, 9, 6), datetime(2011, 8, 18, 9, 37), datetime(2011, 8, 18, 9, 37), datetime(2011, 8, 18, 10, 15), datetime(2011, 8, 18, 11, 5), datetime(2011, 8, 18, 11, 6), datetime(2011, 8, 19, 11, 40), datetime(2011, 8, 19, 12, 11), datetime(2011, 8, 19, 12, 54), datetime(2011, 8, 19, 12, 58), datetime(2011, 8, 19, 14, 31), datetime(2011, 8, 19, 14, 35), datetime(2011, 8, 19, 15, 27), datetime(2011, 8, 22, 9, 0), datetime(2011, 8, 22, 9, 50), datetime(2011, 8, 22, 11, 0), datetime(2011, 8, 22, 11, 10), datetime(2011, 8, 22, 11, 20), datetime(2011, 8, 22, 11, 35), datetime(2011, 8, 22, 12, 48), datetime(2011, 8, 22, 13, 20), datetime(2011, 8, 22, 13, 50), datetime(2011, 8, 22, 13, 56), datetime(2011, 8, 24, 11, 20), datetime(2011, 8, 24, 11, 52), datetime(2011, 8, 24, 13, 0), datetime(2011, 8, 28, 11, 50), datetime(2011, 8, 28, 11, 54), datetime(2011, 8, 29, 3, 38), datetime(2011, 8, 29, 3, 57), datetime(2011, 8, 29, 4, 5), datetime(2011, 8, 29, 13, 49), datetime(2011, 8, 30, 4, 56), datetime(2011, 9, 1, 14, 1), datetime(2011, 9, 3, 3, 0), datetime(2011, 9, 4, 13, 22), datetime(2011, 9, 5, 12, 30), datetime(2011, 9, 5, 12, 50), datetime(2011, 9, 5, 13, 39), datetime(2011, 9, 5, 13, 41), datetime(2011, 9, 9, 11, 30), datetime(2011, 9, 17, 2, 43), datetime(2011, 9, 17, 2, 45, 1), datetime(2011, 9, 18, 13, 18, 1), datetime(2011, 9, 18, 13, 55, 1), datetime(2011, 9, 19, 3, 22, 1), datetime(2011, 9, 24, 18, 45, 1), datetime(2011, 9, 29, 12, 28), datetime(2011, 9, 30, 14, 40, 47), datetime(2011, 10, 5, 11, 37), datetime(2011, 10, 6, 8, 40), datetime(2011, 10, 6, 10, 15), datetime(2011, 10, 22, 7, 4), datetime(2011, 10, 26, 12, 0), datetime(2011, 10, 26, 15, 56, 23), datetime(2011, 10, 26, 16, 38), datetime(2011, 10, 26, 13, 30), datetime(2011, 10, 26, 16, 53), datetime(2011, 10, 31, 13, 42), datetime(1970, 1, 1, 0, 0), datetime(1970, 1, 1, 0, 0), datetime(1970, 1, 1, 0, 0), datetime(2011, 11, 3, 12, 47), datetime(2011, 11, 7, 11, 42)]

def convertDataToMinuteOffsets(data, startAt, clipAt):
    for item in data:
        if item < startAt or item >= clipAt:
            continue
        yield long(((item - startAt).total_seconds()) / 60)


def generateImpulse(sampleCount, beta):
    samples = numpy.zeros(sampleCount)
    stepSize = 2./sampleCount
    #for i in itertools.count(round(-sampleCount/2), round(sampleCount/2)):
    #
    #samples[sampleCount/2] = 1
    for i in xrange(sampleCount):
        x = i * stepSize - 1.0
        samples[i] = math.exp(-x*x/beta)
    return samples

def addDataPoint(offset, samples, impulse):
    left = offset - len(impulse)/2
    if left < 0:
        impulseLeft = -left
        left = 0
    else:
        impulseLeft = None
    right = offset + len(impulse)/2
    if right >= len(samples):
        impulseRight = len(samples)-(right+1)
        right = len(samples) - 1
    else:
        impulseRight = None
    if impulseLeft is None and impulseRight is None:
        samples[left:right] += impulse
    else:
        samples[left:right] += impulse[impulseLeft:impulseRight]

def addDataPoints(data, samples, impulse):
    for item in data:
        addDataPoint(item, samples, impulse)

def generateLowpass(nyquist, cut, transition, minAtt, maxAtt):
    print("generating lowpass: nyquist={4} 1/minute; cut={0} 1/minute; transition={1} 1/minute; min att={2} dB; max att={3} dB".format(cut, transition, minAtt, maxAtt, nyquist))
    return signal.iirdesign((cut - transition * 0.5) / nyquist, (cut + transition * 0.5) / nyquist, maxAtt, minAtt)
    # return signal.iirfilter(13, cut / nyquist, btype='lowpass')


def generateHighpass(nyquist, cut, transition, minAtt, maxAtt):
    print("generating highpass: nyquist={4} 1/minute; cut={0} 1/minute; transition={1} 1/minute; min att={2} dB; max att={3} dB".format(cut, transition, minAtt, maxAtt, nyquist))
    return signal.iirdesign((cut + transition * 0.5) / nyquist, (cut - transition * 0.5) / nyquist, maxAtt, minAtt)
    #return signal.iirfilter(13, cut / nyquist, btype='highpass')

def generateBandpass(nyquist, stopBefore, stopAfter, transition, minAtt, maxAtt):
    return signal.iirdesign(
        (
            stopBefore + transition / 2.,
            stopAfter - transition / 2.
        ),
        (
            stopBefore - transition / 2.,
            stopAfter + transition / 2.
        ),
        maxAtt,
        minAtt
    )
        
    #return signal.iirfilter(13, (stopBefore / nyquist, stopAfter / nyquist), btype='bandpass')

nyquist = 0.5

def mapFreq(nyquist, resultCount, freq):
    offset = 0
    return (freq/nyquist)*resultCount - offset

def mapX(nyquist, resultCount, x):
    return (float(x)/resultCount)*nyquist
    
def processData(data, startAt, clipAt, impulse):
    sampleCount = (clipAt - startAt).total_seconds() / 60
    samples = numpy.zeros(sampleCount)
    dataMinutes = list(convertDataToMinuteOffsets(data, startAt, clipAt))
    addDataPoints(dataMinutes, samples, impulse)
    return samples, sampleCount

def calculateFFT(samples, sampleCount, nyquist, maxFreq):
    # filterConfig = generateHighpass(0.5, 1./(60*24*28), 1./(60*24*112), 30, 5)
    # samples = signal.lfilter(filterConfig[0], filterConfig[1], samples)
    dataCount = mapFreq(nyquist, sampleCount/2, maxFreq)
    fft = numpy.dual.fft(samples)
    magnitude = numpy.abs(fft[:dataCount])
    phase = numpy.angle(fft[:dataCount])
    return magnitude, phase, sampleCount/2

def calculateFrequencyBands(nyquist, resultCount):
    bandFreqs = [
        1./(15),
        1./(30),
        1./(60),
        1./(60*3),
        1./(60*6),
        1./(60*12),
        1./(60*24),
        1./(60*24*1.75),
        1./(60*24*3.5),
        1./(60*24*7),
        1./(60*24*14),
        1./(60*24*28),
    ]
    
    bands = [mapFreq(nyquist, resultCount, freq) for freq in bandFreqs]
    bandNames = ["15min", "30min", "1h", "3h", "6h", "12h", "1d", "1.75d", "3.5d", "7d", "14d", "28d"]
    
    bandDict = dict(itertools.izip(
        bandNames,
        bandFreqs
    ))
    return bandFreqs, bands, bandNames, bandDict


def createFigure(magnitude, phase, xBands, xBandNames):
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    
    ax.set_xscale('log', basex=2)
    ax.set_xticks(xBands)
    ax.set_xticklabels(xBandNames)
    ax.grid()
    ax.plot(magnitude)
    return fig

def showFigure(fig, delete=True):
    plt.show()
    if delete:
        plt.close(fig)

def findPeak(data, sigma):
    maxY = float("-inf")
    maxX = 0
    for x, y in itertools.izip(itertools.count(0), data):
        if y > maxY:
            maxX = x
            maxY = y
    
    #lowCut = 
    #for x, y in itertools.izip(itertools.count(0), data):
    return maxX, maxY

def detectPeak(magnitude, nyquist, resultCount, bandDict, tolerance=0.1):
    skip = mapFreq(nyquist, len(magnitude)/2, 1./(60*24*28)-1)
    magnitude = magnitude[skip:]
    maxX, maxY = findPeak(magnitude, 0.1)
    maxFreq = mapX(nyquist, resultCount, maxX)
    for name, band in bandDict.iteritems():
        bandMin = band - band*tolerance
        bandMax = band + band*tolerance
        if (maxFreq >= bandMin) and (maxFreq < bandMax):
            return maxFreq, maxY, name
    return maxFreq, maxY, None
    
def selectDataMatches(sortedData, startIndex, stepDelta, toleranceSeconds, maxSkip=0):
    nextAt = sortedData[startIndex]
    remainingSkips = maxSkip
    def check(item, nextAt):
        delta = nextAt - item
        return abs(delta.total_seconds()) <= toleranceSeconds
    
    for item in sortedData[startIndex:]:
        while not check(item, nextAt) and remainingSkips > 0:
            remainingSkips -= 1
            nextAt += stepDelta
        if check(item, nextAt):
            yield item
            nextAt += stepDelta
        else:
            print("Run broken, all skips used, returning")
            return

def process_1d_peak(data):
    selection = []
    stepDelta = timedelta(days=1)
    tolerance = 60*60 # one hour
    for i, item in itertools.izip(itertools.count(0), data):
        if item in selection:
            continue
        selection += list(selectDataMatches(data, i, stepDelta, tolerance, 3))
    print(selection)
    data2 = list(data)
    for item in selection:
        data.remove(item)
    print(data2)
    print(len(selection))
    print(len(data2))
    

def processPeak(data, bandName):
    pass

data.sort()
impulse = generateImpulse(4096, 0.01)
samples, sampleCount = processData(data, startAt, clipAt, impulse)
magnitude, phase, resultCount = calculateFFT(samples, sampleCount, nyquist, 1./(7.5))
frequencyBands, xBands, bandNames, bandDict = calculateFrequencyBands(nyquist, resultCount)
showFigure(createFigure(magnitude, phase, xBands, bandNames))
peak = detectPeak(magnitude, nyquist, resultCount, bandDict)

if peak[2] == "1d":
    process_1d_peak(data)
else:
    print("Peak frequency {2} of peak with height {1} is in unknown band: {0}".format(peak[2], peak[0], peak[1]))
