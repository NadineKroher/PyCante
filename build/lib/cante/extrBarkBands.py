import math
from scipy import fft
from numpy import max, multiply, hamming

def extrBarkBands(samples):

    '''
    Extracts the energy of the lower 12 bark bands.

    E. Zwicker and E. Terhardt: Analytical expressions for critical band
    rate and critical bandwidth as a function of frequency. Journal of the
    Acoustic Society of America, vol. 68, 1980, pp 1523-1525

    :param samples: audio file samples with fs 44.1kHz
    :return: array bb holding the bark band energies for each frame
    '''

    # PARAMETERS
    fs = 44100
    wSize = 1024
    hSize = 1024
    bands = [0.0, 50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 510.0, 630.0, 770.0, 920.0, 1080.0, 1270.0]
    fftSize = 1024

    # INIT
    window = hamming(wSize) # Hanning window
    numFrames = int(math.floor(float(len(samples))/float(hSize)))
    numBands = len(bands)-1
    bb =[]
    freqScale = (float(fs)*0.5) / float((wSize-1))

    startBin = []
    endBin = []
    for ii in range(0,numBands):
        startBin.append(int(round(bands[ii]/freqScale+0.5)))
        endBin.append(int(round(bands[ii+1]/freqScale+0.5)))

    # FRAME-WISE BARK BAND EXTRACTION
    for i in range(0,numFrames):
        frame = samples[i*hSize:i*hSize+wSize]
        if len(frame)<wSize:
            break
        spec = abs(fft(frame*window)) / fftSize
        b = []
        for ii in range(0,numBands):
            b.append(sum(spec[startBin[ii]:endBin[ii]]*spec[startBin[ii]:endBin[ii]]))
        if max(b) > 0:
            b = b/max(b)
        bb.append(b)

    return bb