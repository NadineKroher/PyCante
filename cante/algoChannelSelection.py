from scipy import fft, conj, subtract
from numpy import hanning, mean
import math

def algoChannelSelection(left, right):

    ''' Algorithm which automatically selects the channel with dominant vocals from a stereo flamenco recording
    based on spectral band energies as described in section 2-A-I of

    Kroher, N. & Gomez, E. (2016). Automatic Transcription of Flamenco Singing from Polyphonic Music Recordings.
    ACM / IEEE Transactions on Audio, Speech and Language Processing, 24(5), pp. 901-913.

    :param left: samples of the left audio channel in 44.1kHz
    :param right: samples of the right audio channel in 44.1kHz
    :return: index of the dominant vocal channel (0 = left, 1 = right)
    '''

    # PARAMETERS
    fs = 44100 # sample rate
    wSize = 2048 # window size in samples
    hSize = 2048 # hop size in samples
    fftSize = 2048 # FFT size
    freqGuitLow = 80.0 # lower bound for guitar band
    freqGuitHigh = 400.0 # upper bound for guitar band
    freqVocLow = 500.0 # lower bound for vocal band
    freqVocHigh = 6000.0 # higher bound for vocal band

    # INIT
    window = hanning(wSize)
    numFrames = int(math.floor(float(len(left))/float(wSize)))
    # bin indices corresponding to freqeuncy band limits
    indGuitLow = int(round((freqGuitLow/fs)*fftSize))
    indGuitHigh = int(round((freqGuitHigh/fs)*fftSize))
    indVocLow = int(round((freqVocLow/fs)*fftSize))
    indVocHigh = int(round((freqVocHigh/fs)*fftSize))

    # frame-wise computation of the spectral band ratio
    sbrL = []
    sbrR = []
    for i in range(0,numFrames-100):
        frameL = left[i*hSize:i*hSize+wSize]
        specL = fft(frameL*window) / fftSize
        specL = abs(specL * conj(specL))
        guitMag = sum(specL[indGuitLow:indGuitHigh],0)
        vocMag = sum(specL[indVocLow:indVocHigh],0)
        sbrL.append(20*math.log10(vocMag/guitMag))
        frameR = right[i*hSize:i*wSize+wSize]
        specR = fft(frameR*window) / fftSize
        specR = abs(specR * conj(specR))
        guitMag = sum(specR[indGuitLow:indGuitHigh],0)
        vocMag = sum(specR[indVocLow:indVocHigh],0)
        sbrR.append(20*math.log10(vocMag/guitMag))

    # select channel based on mean SBR
    if mean(sbrL)>=mean(sbrR):
        ind = 0
    else:
        ind = 1

    return ind