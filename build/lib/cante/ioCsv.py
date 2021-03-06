''' Auxiliary functions for csv file reading and writing'''

import csv
from numpy import genfromtxt

def importF0(filename):

    '''
    Reads a fundamental frequency contour from a csv file, i.e. as generated by sonic visualizer
    (www.sonicvisualizer.org) or sonic annotator (http://www.vamp-plugins.org/sonic-annotator/).
    The hop size is required to be of 128 samples for audio files with 44.1kHz sample rate.
    :param filename: path to the file to be read
    :raises: raises an error if the detected hop size does not match 128 samples
    :return: f0: fundamental frequency contour in Hz
    '''

    F = genfromtxt(filename,delimiter=',')
    f0 = F[:,1]
    f0[f0<0]=0
    t = F[:,0]
    deltaT = t[1]-t[0]
    hopSize = round(deltaT * 44100)
    if hopSize != 128:
        print('ERROR: Detected hop size is %d samples',hopSize)
        print('Required: 128 samples')
    return f0


def writeToCsv(notes,filename):

    '''
    Writes the output array of the transcription algorithm to a csv file in the following format:
    <note onset [seconds]>, <note duration [seconds]>, <MIDI pitch>

    :param notes: array containing note events
    :param filename: csv file to be written
    :return: NONE
    '''
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerows(notes)

    return
