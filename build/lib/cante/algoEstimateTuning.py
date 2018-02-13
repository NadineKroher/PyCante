from .utils import convertToCents
from .utils import movingAverageBin
from numpy import cos, sin, angle, array
from math import pi

def algoEstimateTuning(f0,startC,endC):

    ''' Algorithm which estimates a tuning frequency for A4 in Hz based on a vocal melody contour and estimated
    note boundaries. Implementation based on the algorithm described in
    K. Dressler and S. Strech, Tuning frequency estimation using circular statistics,
    8th International Conference on Music Information Retrieval,
    2007, pp. 357-360.
    :param f0: estimated vocal melody in Hz, with hopSize 128 at fs 44.1kHz
    :param startC: array containing the start indices of estimated note segments
    :param endC: array containing the end indices of estimated note segments
    :return: fT: estimated A4 tuning frequency in Hz
    '''

    # PARAMETERS
    fRef = 440.0 # reference tuning frequency for A4

    # INIT
    f0Tune = list(f0) # copy of f0 contour from input
    dev = [] # local tuning deviation
    tuningRef = []

    # MAIN ROUTINE
    for i in range(0, len(startC)):
        # segment-wise smoothing
        seg = f0Tune[startC[i]:endC[i]]
        # convert to cents
        seg = convertToCents(seg,fRef)
        seg = movingAverageBin(seg,30)
        # compute local tuning deviation
        for ii in range(0,len(seg)):
            dev.append(seg[ii]-round(seg[ii]/100.0)*100.0)

    # convert to angle representation
    dev = array(dev,dtype=float)
    dev = 2.0 * pi * (dev / 100.0)

    # compute average tuning deviation
    Re = sum(cos(dev))/float(len(dev))
    Im = sum(sin(dev))/float(len(dev))
    TT = angle(Re+Im*1j)

    # convert to cents
    deltaTune = (100.0/(2.0*pi))*TT

    # compute estimated tuning frequency in Hz
    fT = fRef* pow(10.0,deltaTune/(1200.0 * 3.322038403))

    return fT
