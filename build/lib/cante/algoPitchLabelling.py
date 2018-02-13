from cante.ThirdParty.IF_chromagram import IF_chromagram
from numpy import array, histogram, log2, argmax, zeros, arange
from scipy.stats import norm

from .utils import convertToCents, movingAverage


def algoPitchLabelling(_f0,startC,endC,fT,samples):

    '''
    Algorithm to assign MIDI note labels to a given set of note events as described in section 2-B-II of

    Kroher, N. & Gomez, E. (2016). Automatic Transcription of Flamenco Singing from Polyphonic Music Recordings.
    ACM / IEEE Transactions on Audio, Speech and Language Processing, 24(5), pp. 901-913.

    :param _f0: fundamental frequency contour with hop size 128 and fs 44.1kHz
    :param startC: note event start indices
    :param endC: note event end indices
    :param fT: A4 tuning frequency in Hz
    :param samples: audio samples with fs 44.1kHz
    :return: notes: array in which rows correspond to note events; first element -> onset time [seconds], second element
            --> note duration [seconds], third element --> MIDI pitch
    '''

    # PARAMETERS
    hSizePitch = 128.0
    fs = 44100.0

    # EXTRACT AVERAGE CHROMA
    _h = IF_chromagram(samples, fT)

    # INIT
    notes = []
    binCenters = list(arange(-2400,2400,100))
    histBins = list(arange(-2450,2450,100))
    h = list(_h)
    pcp = h+h+h+h
    f0 = array(_f0)

    # MAIN ROUTINE
    for i in range(0,len(startC)):

        # get a segment
        seg = f0[startC[i]:endC[i]]

        if len(seg) < 25:
            continue

        # convert to cents
        seg = convertToCents(seg,fT)

        # segment-wise smoothing
        filterLen = min(25,len(seg))
        seg = movingAverage(seg,filterLen)

        # cut off ends
        l = float(len(seg))
        seg = seg[int(max(1,round(0.2*l))):int(max(1,(round(0.8*l))))]

        # local histogram
        localHist = histogram(seg,histBins)
        localHist = array(localHist[0],dtype=float)
        localHist = localHist / sum(localHist)

        # introduce "leakage"
        sumHist = zeros((len(localHist),len(localHist)))
        for j in range(0,len(localHist)):
            sumHist[j:]=norm(j, 0.5).pdf(range(0,len(localHist)))*localHist[j]
        pP = sum(sumHist)
        localHist = pP
        localHist = localHist / sum(localHist)

        # introduce pitch class probabilities
        localHist = localHist * pcp

        # assign label
        centLabel = binCenters[argmax(localHist)]
        freqLabel = fT*pow(10.0,float(centLabel)/(1200.0*3.322038403))
        mPitch = int(round(12.0*log2(freqLabel/440.0)+69.0))
        sTime = startC[i] * hSizePitch/fs
        duration = (endC[i]-startC[i]) * hSizePitch/fs

        # add note to array
        notes.append([sTime, duration, mPitch])

    return notes
