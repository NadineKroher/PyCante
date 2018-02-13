from .extrBarkBands import extrBarkBands
from numpy import mean, cov, array
from scipy.stats import multivariate_normal
from .utils import movingAverageBin, findSegments

def algoContourFiltering(_f0, audioSamples):

    ''' Algorithm to filter out pitch contour segments which originate from the guitar accompaniments
     as described in section 2-A-III of

    Kroher, N. & Gomez, E. (2016). Automatic Transcription of Flamenco Singing from Polyphonic Music Recordings.
    ACM / IEEE Transactions on Audio, Speech and Language Processing, 24(5), pp. 901-913.

    :param _f0: estimated predominant melody in Hz, computed with hopSize 128 at fs 44.1kHz
    :param audio signal with fs 44.1kHz
    :return: f0: estimated vocal melody in Hz, with hopSize 128 at fs 44.1kHz
    '''

    # init
    f0 = array(_f0)
    hopSize = 1024
    hopSizePitch = 128
    fs = 44100
    resFactor = int(hopSize/hopSizePitch)

    # extract bark bands
    bb = extrBarkBands(audioSamples)

    # adjust array length
    aLen = min([len(bb)*resFactor, len(f0)])
    bb = bb[0:int(aLen*resFactor)]
    f0 = f0[0:int(aLen)]

    # gather bark bands for voiced and unvoiced frames (initial estimation)
    Bu = []
    Bv = []
    for i in range (0,len(bb)):
        b = bb[i]
        if f0[i*resFactor] > 0:
            Bv.append(b)
        else:
            Bu.append(b)

    # fit multivariate Gaussian distributions to both data sets
    meanBu = mean(Bu, axis=0)
    covBu = cov(Bu, rowvar=0, ddof=1)
    meanBv = mean(Bv, axis=0)
    covBv = cov(Bv, rowvar=0, ddof=1)

    # evaluate PDF for each frame
    voc = []
    for i in range (0,len(bb)):
        b = bb[i]
        probVoc = multivariate_normal.pdf(b,meanBv,covBv)
        probGuit = multivariate_normal.pdf(b,meanBu,covBu)
        if probVoc > probGuit:
            for ii in range(0,resFactor):
                voc.append(1)
        else:
            for ii in range(0,resFactor):
                voc.append(0)

    # smooth vocal detection
    vvoc = movingAverageBin(voc,345)

    # convert to binary sequence
    for i in range(0,aLen):
        if vvoc[i] > 0.5:
            voc[i] = 1
        else:
            voc[i] = 0

    # get start and end segments
    startC, endC = findSegments(f0)

    # eliminate contours classified as unvoiced
    for i in range(0,len(startC)):
        vConf = sum(voc[startC[i]:endC[i]])
        if vConf == 0:
            for i in range(startC[i],min(endC[i]+2,len(f0))):
                f0[i] = 0

    return f0
