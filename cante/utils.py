''' Various auxiliary functions '''
from numpy import ones, convolve, array, log10, multiply, divide, hanning, r_


def movingAverage(input,length):

    '''
    Moving average filter.
    :param input: input array
    :param length: filter length
    :return: filtered signal
    '''

    x = array(input)
    s=r_[x[length-1:0:-1],x,x[-1:-length:-1]]
    w = hanning(length)

    return convolve(w/w.sum(),s,mode='valid')


def movingAverageBin(input,length):

    """
    Moving average filter (alternative implementation).
    :param input: input array
    :param length: filter length
    :return: filtered signal
    """

    length = min(length,len(input))
    window = ones(int(length))/float(length)

    return convolve(input, window, 'same')


def convertToCents(_input, fRef):

    '''
    Covert a pitch sequence in Hz to cents relative to a given reference frequency
    :param _input: input sequence in Hz
    :param fRef: reference frequency
    :return: sequence in cents
    '''
    input = array(_input,dtype=float)
    input = divide(input,fRef)
    input = log10(input)
    output = multiply(input, 1200*3.32204)

    return output

def findSegments(f0):

    '''
    Finds sections of consecutive voiced frames in a fundamental frequency contour.
    :param f0: fundamental frequency contour with hop size 128 at fs 44.1kHz
    :return: startC: section start indices, endC: section end indices
    '''
    startC = []
    endC = []
    if f0[0]>0:
        startC.append(0)
    for i in range(0,len(f0)-1):
        if (abs(f0[i+1]) > 0) and (abs(f0[i])<=0):
            startC.append(i+1)
        if (abs(f0[i+1]) <= 0) and (abs(f0[i]>0)):
            endC.append(i)

    if len(endC) < len(startC):
        endC.append(len(f0))

    return startC, endC

