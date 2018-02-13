''' Auxiliary functions for reading audio files '''

import scipy.io.wavfile
from numpy import ndarray, multiply

def loadWaveAudio(filename):
    """ loads samples of a 16Bit 44.1kHz wav audio file for processing
    :param filename: path to audio file
    :return: dictionary with fields:
            - 'left': samples of left audio channel
            - 'right': samples of right audio channel
            - 'numChannels': number of audio channels
            For mono files, 'left' and 'right' contain the same data.
    :raises: - raises an error if the file format is not 16Bit 44.1 kHz .wav audio
             - scipy.io.wavfile throws a warning if the file contains meta-data which cannot be decoded
    """
    # check if this is a wav file
    if not filename.endswith('.wav'):
        print('ERROR: Wrong input file format!')
        print('Required: .wav')

    # read audio samples and sample rate
    [fs, data] = scipy.io.wavfile.read(filename)

    # check file format
    if data.dtype != 'int16' or fs != 44100:
        print('ERROR: Wrong input file format!')
        print('bit depth = %d, sample rate = %d' %(data.dtype, fs))
        print('Required: 16 Bit, 44100 Hz')

    # get number of channels
    if isinstance(data[0],ndarray):
        numChannels = 2
    else:
        numChannels = 1

    # split channels and convert to float
    if numChannels == 2:
        left = multiply(data[:,0],1.0/pow(2,15))
        right = multiply(data[:,numChannels-1],1.0/pow(2,15))
    else:
        left = multiply(data,1.0/pow(2,15))
        right = multiply(data,1.0/pow(2,15))

    return {'left':left, 'right':right, 'numChannels': numChannels}

