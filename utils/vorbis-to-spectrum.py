#!/usr/bin/python2
# encoding=utf-8
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as pyplot
import matplotlib.colors as colors
import matplotlib.cm as cm
import ogg.vorbis
import sys
import array
import itertools
import math
import numpy
import scipy.signal as signal
import scikits.samplerate as samplerate
import argparse
import matplotlib.mlab as mlab
from numpy import ma
import matplotlib.cbook as cbook
import os.path

class MyNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, clip=False, rmin=0., rmax=0., staticrange=None):
        colors.Normalize.__init__(self, vmin, vmax, clip)
        self.rmin = rmin
        self.rmax = rmax
        self.staticrange = staticrange
    
    def __call__(self, value, clip=None):
        if clip is None:
            clip = self.clip

        if cbook.iterable(value):
            vtype = 'array'
            val = ma.asarray(value).astype(numpy.float)
        else:
            vtype = 'scalar'
            val = ma.array([value]).astype(numpy.float)
        
        if self.staticrange is None:
            self.autoscale_None(val)
            vmin, vmax = self.vmin, self.vmax
        else:
            self.vmin, self.vmax = None, None
            self.autoscale_None(val)
            vmin, vmax = self.vmax - self.staticrange, self.vmax
        if vmin > vmax:
            raise ValueError("minvalue must be less than or equal to maxvalue")
        elif vmin==vmax:
            result = 0.0 * val
        else:
            vmin = float(vmin)
            vmax = float(vmax)
            rmin = float(self.rmin)
            rmax = float(self.rmax)
            if clip:
                mask = ma.getmask(val)
                val = ma.array(np.clip(val.filled(vmax), vmin, vmax),
                                mask=mask)
            result = (val-vmin) * ((rmax-rmin) / (vmax-vmin)) + rmin
        if vtype == 'scalar':
            result = result[0]
        return result
#m = cm.get_cmap()
#m = MySpectrumColors("myspectrum")
#print(repr(m))
#print(dir(m))
#print(m(1.2))
#sys.exit(0)

class SpectrumRenderer(object):
    def __init__(self, channels, sampleRate, 
            minFreq=0., 
            maxFreq=None, 
            usedBScale=True, 
            valueRange=(None, None), 
            NFFT=2048, 
            overlap=1536, 
            resampleWithSeparateLowpass=True,
            lowpass=None,
            lowpassTransition=None,
            lowpassMaxAttenuation=6.,
            lowpassMinAttenuation=60.,
            staticRange=None):
        
        self.channels = channels
        self.sampleRate = sampleRate
        self.NFFT = NFFT
        self.overlap = overlap
        if self.sampleRate < 2:
            raise ValueError("Invalid sample rate: {0}".format(self.sampleRate))
        self.nyquist = float(self.sampleRate / 2.)
        self.minFreq = minFreq
        if self.minFreq != 0.:
            raise ValueError("Frequency shifting is currently not supported!")
        self.maxFreq = maxFreq
        if self.maxFreq is None:
            self.maxFreq = self.nyquist
        if self.maxFreq > self.nyquist:
            print >>sys.stderr, "{0}: warning: clamped max-freq to nyquist frequency {1}".format(os.path.basename(sys.argv[0]), self.nyquist)
        if self.maxFreq <= 2.:
            raise ValueError("Invalid max freq: {0}".format(self.maxFreq))
        
        self.newSampleRate = None
        self.filtera = None
        self.filterb = None
        if self.maxFreq != self.nyquist:
            self.newSampleRate = int(self.maxFreq * 2.)
            if resampleWithSeparateLowpass:
                self.filterb, self.filtera = self.generateLowpass(self.maxFreq, lowpassTransition, lowpassMinAttenuation, lowpassMaxAttenuation)
        elif args.lp is not None:
            self.filterb, self.filtera = self.generateLowpass(lowpass, lowpassTransition, lowpassMinAttenuation, lowpassMaxAttenuation)
            
        self.usedBScale = usedBScale
        self.valueRange = valueRange
        self.staticRange = staticRange
        
    def generateLowpass(self, cut, transition, minAtt, maxAtt):
        print("generating lowpass: cut={0} Hz; transition={1} Hz; min att={2} dB; max att={3} dB".format(cut, transition, minAtt, maxAtt))
        return signal.iirdesign((cut - transition * 0.5) / self.nyquist, (cut + transition * 0.5) / self.nyquist, maxAtt, minAtt)
    
    def prepareData(self):
        if self.newSampleRate is not None:
            resamplingFactor = float(self.newSampleRate)/float(self.sampleRate)
        elif self.filterb is None:
            print("skipping data preparation, nothing to do")
            return
        
        newChannels = [None for x in xrange(len(self.channels))]
        for i, channel in itertools.izip(xrange(len(self.channels)), self.channels):
            print("channel {0}".format(i))
            newData = channel
            if self.filterb is not None:
                print("  lowpass")
                newData = signal.lfilter(self.filterb, self.filtera, channel)
            if self.newSampleRate is not None:
                print("  resampling")
                newData = samplerate.resample(numpy.array(channel), resamplingFactor, 'sinc_best' if self.filterb is None else 'sinc_medium')
            newChannels[i] = newData
        self.channels = newChannels
        if self.newSampleRate is not None:
            self.sampleRate = self.newSampleRate
            
    def getCmap(self):
        p1, p2, p3, p4, p5 = 1./6., 1./3., 0.5, 2./3., 5./6.
        return colors.LinearSegmentedColormap("myspectrum", {
            'red':
                [   (0., 0., 0.),
                    (p1, 0., 0.),
                    (p2, 0., 0.),
                    (p3, 0., 0.),
                    (p4, 1., 1.),
                    (p5, 1., 1.),
                    (1., 1., 1.)    ],
            
            'green':
                [   (0., 0., 0.),
                    (p1, 0., 0.),
                    (p2, 1., 1.),
                    (p3, 1., 1.),
                    (p4, 1., 1.),
                    (p5, 0., 0.),
                    (1., 1., 1.)    ],
                    
            'blue':
                [   (0., 0., 0.),
                    (p1, 1., 1.),
                    (p2, 1., 1.),
                    (p3, 0., 0.),
                    (p4, 0., 0.),
                    (p5, 0., 0.),
                    (1., 1., 1.)    ],
        }, 512)
        
    def getNormalizer(self):
        return MyNormalize(self.valueRange[0], self.valueRange[1], rmin=1./6., rmax=5./6., staticrange=self.staticRange)
            
    def specgram(self, ax, channel):
        Pxx, freqs, bins = mlab.specgram(channel, self.NFFT, self.sampleRate, mlab.detrend_none,
             mlab.window_hanning, self.overlap, None, 'onesided', None)
        
        if self.usedBScale:
            Z = 10. * numpy.log10(Pxx)
        else:
            Z = Pxx
        Z = numpy.flipud(Z)

        xmin, xmax = 0, numpy.amax(bins)
        extent = xmin, xmax, freqs[0], freqs[-1]
        norm = self.getNormalizer()
        im = ax.imshow(Z, cmap=self.getCmap(), norm=norm, extent=extent)
        return im
    
    def renderGraphs(self, ax_iterator):
        for i, channel, ax in itertools.izip(xrange(len(self.channels)), self.channels, ax_iterator):
            print("channel {0}".format(i))
            print("  calculating new specgram")
            #ax.specgram(channel, NFFT=self.NFFT, Fs=self.sampleRate, noverlap=self.overlap)
            im = self.specgram(ax, channel)
            ax.axis('tight')
            ax.set_title('Channel {0}'.format(i), weight='demi')
            ax.set_ylabel('Frequency / Hz', weight='bold')
            if i == len(self.channels)-1:
                ax.set_xlabel('Time / s', weight='bold')
            ax.grid(True, color=(0.9, 0.9, 0.9, 1.0), linewidth=1.)
            yield im
    
def readPCM(vf, maxPCM=None):
    def printStatus(status):
        print("reading pcm samples: {0:5.1f}%".format(status * 100.0))
    printCounter = 0
    totalL = long(maxPCM)
    total = float(totalL)
    while vf.pcm_tell() < totalL:
        buf, s, o = vf.read()
        yield buf[:s]
        printCounter += 1
        if printCounter >= 1000:
            printCounter = 0
            printStatus(float(vf.pcm_tell()) / total)

def decodeVorbisToChannels(file, skip, duration):
    vf = ogg.vorbis.VorbisFile(file)
    vi = vf.info()
    sampleRate = vf.info().rate
    channelCount = vf.info().channels
    
    vf.pcm_seek(0)
    if args.duration is not None:
        vf.time_seek(skip + duration)
        maxPCM = vf.pcm_tell()
    else:
        maxPCM = vf.pcm_total()
    vf.time_seek(skip)
    startTime = vf.time_tell()
    
    data = array.array('h')
    for buff in readPCM(vf, maxPCM):
        data.fromstring(str(buff))
    
    maxValue = 32768.
    seconds = vf.time_tell() - startTime
    return (sampleRate, seconds, [[float(v) / maxValue for v in data[x::channelCount]] for x in xrange(channelCount)])

if __name__=='__main__':
    
    def powerOfTwo(i):
        i = int(i)
        l = math.log(i, 2)
        if math.floor(l) != l:
            raise ValueError('Must be power of two: {0}'.format(i))
        return i
        
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Create a spectrum view from an ogg/vorbis file.",
        epilog=u"Available filters:\n {0}".format(u"\n ".join(u"{0}:\n  {1}".format(filterType, samplerate.convertor_description(filterType)) for filterType in samplerate.available_convertors()))
    )
    
    inputGroup = parser.add_argument_group("Input settings")
    inputGroup.add_argument(
        dest='infile', 
        metavar='INPUTFILE',
        type=argparse.FileType('rb'),
        help='Input file of type audio/vorbis'
    )
    inputGroup.add_argument('-s', '--skip',
        metavar='SECONDS',
        type=float,
        help='seconds to skip at the start of the file',
        default=0.
    )
    inputGroup.add_argument('-t', '--duration',
        metavar='SECONDS',
        type=float,
        help='how many seconds to capture and process. Leave blank for the whole file. If SECONDS is negative, processing will take place until time_total+SECONDS (that is, -SECONDS seconds before the end of file). This is only approximate.',
        default=None
    )
    
    filterGroup = parser.add_argument_group('Filters and Processing')
    filterGroup.add_argument('--min-freq', 
        metavar='FREQ',
        type=float,
        help='Start frequency of the spectrum in Hz (ignored)',
        default=0.
    )
    group = filterGroup.add_mutually_exclusive_group()
    group.add_argument('--max-freq',
        metavar='FREQ',
        type=float,
        help='End frequency of the spectrum in Hz. If this is below half the sample rate of the input file, automatic resampling will take place. Omit for no resampling. This implies a lowpass with the cut frequency at the given FREQ.'
    )
    group.add_argument('--lp', '--lowpass',
        metavar='FREQ',
        type=float,
        help='Lowpass the signal using the given cut frequency. This will be rejected if --max-freq is given, as --max-freq implies a lowpass already.',
        default=None
    )
    filterGroup.add_argument('--lptb', '--lowpass-transition-band',
        metavar='BANDWIDTH',
        type=float,
        help='Width of the transition band of the lowpass. Defaults to 10%% of the cut frequency if omitted.',
        default=None
    )
    filterGroup.add_argument('--lowpass-min-attenuation',
        metavar='DECIBEL',
        type=float,
        help='Minimum attenuation to achieve beyond the cut frequency.',
        default=60.
    )
    filterGroup.add_argument('--lowpass-max-attenuation',
        metavar='DECIBEL',
        type=float,
        help='Maximum attenuation to achieve below the cut frequency.',
        default=6.
    )
    filterGroup.add_argument('--fft-size',
        metavar='FFTSIZE',
        type=powerOfTwo,
        help='Size of the FFT window. Must be power of two.',
        default=2048
    )
    filterGroup.add_argument('--fft-overlap',
        metavar='FFTOVERLAP',
        type=int,
        help='Overlap of the FFT window. Must be power of two.',
        default=1536
    )
    filterGroup.add_argument('-r', '--resample-filter',
        metavar='NAME',
        type=str,
        help='Uses resampling filter NAME. Default is sinc_medium',
        default='sinc_medium'
    )
    filterGroup.add_argument('-l', '--additional-lowpass',
        action='store_true',
        help='Apply an additional lowpass before resampling. Has only an effect if --max-freq is given and below the nyquist frequency of the input file',
        default=False
    )
    
    spectrumGroup = parser.add_argument_group("Visual settings of the spectrum")
    spectrumGroup.add_argument('-d', '--use-db',
        action='store_true',
        help='Enable spectrum view in dB instead of raw units.',
        default=False
    )
    spectrumGroup.add_argument('--min-range',
        metavar='MIN',
        type=float,
        help='Value of the result spectrum which will map to blue. Leave blank for maximum dynamic range.',
        default=None
    )
    spectrumGroup.add_argument('--max-range',
        metavar='MAX',
        type=float,
        help='Value of the result spectrum wihch will map to red. Leave blank for maximum dynamic range.',
        default=None
    )
    spectrumGroup.add_argument('--static-range',
        metavar='DECIBELS',
        type=float,
        help='The application will always set a static dynamic range of DECIBELS width based on the maximum value found in the spectrum. Specifying --static-range makes --min-range and --max-range useless.',
        default=None
    )
    
    outputGroup = parser.add_argument_group("Output image settings")
    outputGroup.add_argument(
        dest='outfile',
        metavar='OUTFILE',
        help='Where the png goes. Defaults to ./out.png',
        default='out.png'
    )
    outputGroup.add_argument('--dpi',
        metavar='DPI',
        type=float,
        help='Dots per inch of the output image.',
        default=72.
    )
    group = outputGroup.add_mutually_exclusive_group()
    group.add_argument('--channel-height',
        metavar='INCHES',
        type=float,
        help='Height of a channel spectrum in inches',
        default=None,
    )
    group.add_argument('--frequency-height',
        metavar='INCHES',
        type=float,
        help='If this is given, the height allocated for a channel is calculated by taking the bandwidth in kHz and multiplying that with INCHES.',
        default=None
    )
    group.add_argument('--fft-height',
        metavar='INCHES',
        type=float,
        help='Sets the height to INCHES*(FFTSIZE/2.). This is set to 1/DPI if omitted.',
        default=None
    )
    group = outputGroup.add_mutually_exclusive_group()
    group.add_argument('--seconds-width',
        metavar='INCHES',
        type=float,
        help='Width of the output image per input seconds.'
    )
    group.add_argument('--fft-line-width',
        metavar='INCHES',
        type=float,
        help='Width of one fft line in the output image. If not set, it defaults to 1/DPI'
    )
    outputGroup.add_argument('--scale-dpi',
        metavar='FACTOR',
        type=float,
        help='Uses DPI*FACTOR instead of DPI for plot width and height calculations without changing the actual DPI.',
        default=1.
    )
    args = parser.parse_args(sys.argv[1:])
    #print(args)
    #sys.exit(0)
    
    sampleRate, seconds, channels = decodeVorbisToChannels(args.infile, args.skip, args.duration)
    
    args.scaledDPI = args.dpi * args.scale_dpi
    
    if args.frequency_height is not None:
        bandwidth = float(sampleRate) / 2.
        if args.max_freq is not None:
            bandwidth = min(args.max_freq, bandwidth)
        plotHeight = (bandwidth/1000.)*args.frequency_height
    elif args.channel_height is not None:
        plotHeight = args.channel_height
    else:
        plotHeight = args.fft_size/((args.scaledDPI if args.fft_height is None else 1./args.fft_height)*2.)
    height = len(channels) * plotHeight
    
    if args.seconds_width is not None:
        width = seconds * args.seconds_width
    else:
        lineWidth = args.fft_line_width if args.fft_line_width is not None else 1./(args.scaledDPI)
        fftSamples = float(args.fft_size - args.fft_overlap)
        width = lineWidth * float(len(channels[0]))/(fftSamples)
    plotWidth = width
    
    figure = pyplot.figure()
    
    fig = pyplot.figure()
    leftBorder, rightBorder = 1.0,      1.5
    topBorder, bottomBorder = 0.3,      0.5
    vspace = 0.4
    hspace = 0.
    
    width = width + leftBorder + rightBorder + hspace
    height = height + topBorder + bottomBorder + vspace * (len(channels)-1)
    
    fig.set_figwidth(width)
    fig.set_figheight(height)
    
    leftBorder = leftBorder / width
    rightBorder = rightBorder / width
    hspace = hspace / width
    
    topBorder = topBorder / height
    bottomBorder = bottomBorder / height
    vspace = vspace / height
    
    cbarWidth = 0.2 / width
    cbarPadTop = 0.25 / height
    cbarPadLeft = 0.1 / width
    
    plotHeight = plotHeight / height
    plotWidth = plotWidth / width
    
    def ax_iterator(channelCount):
        left = leftBorder
        width = plotWidth
        height = plotHeight
        bottom = 1.0 - (plotHeight + topBorder)
        prevAx = None
        for i in xrange(channelCount):
            #ax = fig.add_subplot(channelCount, 1, offset+i+1, sharex=prevAx)
            ax = fig.add_axes([left, bottom, width, height], sharex=prevAx)
            yield ax
            bottom -= plotHeight + vspace
            prevAx = ax
            
    def colorbar_ax_iterator(channelCount):
        left = leftBorder + plotWidth + cbarPadLeft
        width = cbarWidth
        height = plotHeight
        bottom = 1.0 - (plotHeight + topBorder)
        prevAx = None
        for i in xrange(channelCount):
            ax = fig.add_axes([left, bottom, width, plotHeight])
            yield ax
            bottom -= plotHeight + vspace

    renderer = SpectrumRenderer(channels, sampleRate, 
        maxFreq=args.max_freq,
        usedBScale=args.use_db,
        valueRange=(args.min_range, args.max_range),
        NFFT=args.fft_size,
        overlap=args.fft_overlap,
        resampleWithSeparateLowpass=args.additional_lowpass,
        lowpass=args.lp,
        lowpassTransition=args.lptb if args.lptb is not None else (args.lp if args.lp is not None else (args.max_freq if args.max_freq is not None else float(sampleRate) / 2.)) * 0.1,
        lowpassMinAttenuation=args.lowpass_min_attenuation,
        lowpassMaxAttenuation=args.lowpass_max_attenuation,
        staticRange=args.static_range)
    renderer.prepareData()
    
    for ax, im in itertools.izip(colorbar_ax_iterator(len(channels)), renderer.renderGraphs(ax_iterator(len(channels)))):
        cbar = fig.colorbar(im, cax=ax, format='%.1f dB' if args.use_db else '%.4f', spacing='uniform')
    
    print("rasterizing…")
    fig.savefig(args.outfile, format="png", dpi=args.dpi, transparent=True)
