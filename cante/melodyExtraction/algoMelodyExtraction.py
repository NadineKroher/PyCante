import numpy
from essentia.standard import *

def algoF0Solo(samples):

    '''
    Wrapper for the python bindings of the ESSENTIA implementation of the MELODIA monophonic melody extraction
    algorithm: Estimates a pitch contour from the samples of a monophonic recording with fs 44.1 kHz.

    J. Salamon and E. Gomez, Melody extraction from polyphonic music
    signals using pitch contour characteristics. IEEE Transactions on Audio,
    Speech and Language Processing, vol. 20, no. 6, 2011, pp. 1759-1770.

    :param samples: audio samples with fs 44.1 kHz
    :return: f0: estimated fundamental frequency contour with hopSize 128 at fs 44.1kHz
    '''

    # PARAMETERS
    fs = 44100
    fmin = 120.0
    fmax = 720.0
    wSize = 1024
    hSize = 128

    # extract f0 using ESSENTIA
    input = essentia.array(samples)
    pitchTracker = PitchMelodia(frameSize = wSize, hopSize = hSize, minFrequency = fmin, maxFrequency = fmax, sampleRate = fs)
    f0, pitchConf = pitchTracker(input)

    return f0


def algoF0Acc(samples):

    '''
    Wrapper for the python bindings of the ESSENTIA implementation of the MELODIA predominant melody extraction
    algorithm: Estimates a pitch contour from the samples of a polyphonic recording with fs 44.1 kHz.

    J. Salamon and E. Gomez, Melody extraction from polyphonic music
    signals using pitch contour characteristics. IEEE Transactions on Audio,
    Speech and Language Processing, vol. 20, no. 6, 2011, pp. 1759-1770.

    :param samples: audio samples with fs 44.1 kHz
    :return: f0: estimated fundamental frequency of the predominant melody with hopSize 128 at fs 44.1kHz
    '''

    # PARAMETERS
    fs = 44100
    fmin = 120.0
    fmax = 720.0
    vTol = 0.2
    wSize = 1024
    hSize = 128

    # extract f0 using ESSENTIA
    input = essentia.array(samples)
    pitchTracker = PredominantPitchMelodia(frameSize = wSize, hopSize = hSize, minFrequency = fmin, maxFrequency = fmax, sampleRate = fs, voicingTolerance = vTol, voiceVibrato = True, filterIterations=10)
    f0, pitchConf = pitchTracker(input)

    return f0

