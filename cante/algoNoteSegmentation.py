from math import sqrt

from cante.ThirdParty.detect_peaks import detect_peaks
from numpy import log10, multiply, diff, argmax, mean, divide, std
from scipy.ndimage import gaussian_filter1d

from utils import convertToCents
from utils import findSegments, movingAverage


def algoNoteSegmentation(_f0,samples):

    '''
    Algorithm to segment a fundamental frequency contour f0 extracted into discrete note events based on contour and
    volume characteristics, as described in section 2-B-II of

    Kroher, N. & Gomez, E. (2016). Automatic Transcription of Flamenco Singing from Polyphonic Music Recordings.
    ACM / IEEE Transactions on Audio, Speech and Language Processing, 24(5), pp. 901-913.

    :param _f0: fundamental frequency contour with hop size 128 and fs 44.1kHz
    :param samples: audio samples with fs 44.1kHz
    :return: startC: start indices of note events; endC: end indices of note events
    '''

    # INIT
    f0 = list(_f0)
    hSizeF0 = 128

    # PARAMETERS
    minDurationSam = 25 # min. distance between onsets in f0 samples
    deltaPM = 80 # min. local maxima pitch distance in cents
    sigma = 15 # sigma 1st order of the gaussian derivative filter
    cFmin = 4.0 # minimum height of relevant peaks in the Gaussian derivative filter output
    rLocTh = 6.0 # RMS fluctuation threshold for volume-based segmentation
    zTh = 3.0 # z-score threshold for onset detection from pitch discontinuities

    # initial estimation based on consecutive voiced frames
    startC, endC = findSegments(f0)

    # segment based on difference among local f0 maxima
    for j in range(0,len(startC)):
        if (endC[j]-startC[j]) <= 2*minDurationSam:
            continue
        segment = f0[startC[j] : endC[j]]
        segment = movingAverage(segment,min(15,len(segment)))
        segment = convertToCents(segment,55.0)
        Imax = detect_peaks(segment,0,0)
        lastInd = 0
        for ii in range(0,len(Imax)-1):
            if abs(segment[Imax[ii]]-segment[Imax[ii+1]]) < deltaPM:
                continue
            subseg = segment[Imax[ii]:Imax[ii+1]]
            splitInd = Imax[ii] + argmax(abs(diff(subseg)))
            if splitInd - lastInd < 20 or splitInd < minDurationSam or (len(segment)-splitInd) < minDurationSam:
                continue
            f0[startC[j]+splitInd] = 0
            lastInd = splitInd

    # re-estimate note segments
    startC, endC = findSegments(f0)

    # segment based on Gaussian filter output
    for j in range(0,len(startC)):
        if (endC[j]-startC[j]) <= 4*minDurationSam:
            continue
        segment = f0[startC[j] : endC[j]]
        segment = convertToCents(segment,440.0)
        segment = movingAverage(segment,min(15,len(segment)))
        segment = segment - mean(segment)
        y = gaussian_filter1d(segment,sigma,-1,1)
        Imax = detect_peaks(y,cFmin,minDurationSam)
        for ii in range(0,len(Imax)):
            if Imax[ii] < 60 or (len(segment)-Imax[ii]) < 60:
                continue
            f0[startC[j]+Imax[ii]] = 0


    # re-estimate note segments
    startC, endC = findSegments(f0)

    for j in range(0,len(startC)):
        if (endC[j]-startC[j]) <= 4*minDurationSam:
            continue
        segment = f0[startC[j] : endC[j]]
        segment = convertToCents(segment,440.0)
        segment = movingAverage(segment,min(15,len(segment)))
        segment = segment - mean(segment)
        y = gaussian_filter1d(segment,sigma,-1,1)
        Imax = detect_peaks(-y,cFmin,minDurationSam)
        for ii in range(0,len(Imax)):
            if Imax[ii] < 60 or (len(segment)-Imax[ii]) < 60:
                continue
            f0[startC[j]+Imax[ii]] = 0

    # re-estimate note segments
    startC, endC = findSegments(f0)

    # segment based on volume discontinuities
    for j in range(0,len(startC)):
        # skip short segments
        if (endC[j]-startC[j]) <= 4*minDurationSam:
            continue
        # rms corresponding to current segment
        rms = []
        for ii in range(0,endC[j]-startC[j]):
            sSam = (startC[j]+ii)*hSizeF0-round(0.5*float(hSizeF0))
            sSam = max(0,sSam)
            eSam = (startC[j]+ii)*hSizeF0+round(0.5*float(hSizeF0))
            eSam = min(eSam, len(samples))
            w = samples[int(sSam):int(eSam)]
            w = multiply(w,w)
            rms.append(sqrt(mean(w)))

        # smooth
        rms = movingAverage(rms,min(15,len(rms)))

        # compute dB relative to surrounding 100 samples
        relRms = []
        for ii in range(50,len(rms)-50):
            r = -20*log10(rms[ii]/mean(rms[ii-50:ii+49]))
            relRms.append(r)
        # segment at peaks
        Imax = detect_peaks(relRms,rLocTh,minDurationSam)
        for ii in range(0,len(Imax)):
            Imax[ii] += 50
            if Imax[ii] < minDurationSam or (len(rms)-Imax[ii]) < minDurationSam:
                continue
            f0[startC[j]+Imax[ii]] = 0

    # re-estimate note segments
    startC, endC = findSegments(f0)

    # segment based on pitch discontinuities
    for j in range(0,len(startC)):
        # skip short segments
        if (endC[j]-startC[j]) <= 4*minDurationSam:
            continue
        segment = f0[startC[j]:endC[j]]
        segment = convertToCents(segment,55.0)
        segment = movingAverage(segment,min(15,len(segment)))
        segment = segment - mean(segment)

        # compute z score
        zs = divide(segment,-1*std(segment))

        # segment at peaks
        Imax = detect_peaks(zs,zTh,minDurationSam)
        for ii in range(0,len(Imax)):
            if Imax[ii] < minDurationSam or (len(zs)-Imax[ii]) < minDurationSam:
                continue
            f0[startC[j]+Imax[ii]] = 0

    # re-estimate note segments
    startC, endC = findSegments(f0)

    return startC, endC