from . import *
import time
import os

def AST(filename, acc=True, f0_file=False):

    '''
    Auxiliary method for transcription of a single file. See "transcribe" for a detailed
    description.
    '''
    # display current file
    print('transcribing %s ...' % filename)

    # time tic
    startTime = time.time()

    # load audio file
    audio = loadWaveAudio(filename)

    # select channel if it is a stereo file
    if audio['numChannels'] == 2:
        print('channel selection')
        channel = algoChannelSelection(audio['left'],audio['right'])
        if channel == 0:
            samples = audio['left']
        else:
            samples = audio['right']
    else:
        samples = audio['left']

    # vocal melody extraction
    if not f0_file:
        print('vocal melody extraction')
        if acc:
            # predominant melody extraction
            f0 = algoF0Acc(samples)

        else:
            # monophonic melody extraction
            f0 = algoF0Solo(samples)
    else:
        f0 = importF0(filename[0:len(filename)-3]+'csv')

    # contour filtering
    if acc:
        print('contour filtering')
        f0 = algoContourFiltering(f0,samples)

    # note segmentation
    print('note segmentation')
    onsets, offsets = algoNoteSegmentation(f0,samples)

    # estimate tuning
    print('tuning estimation')
    fT = algoEstimateTuning(f0, onsets, offsets)

    # pitch labelling
    print('pitch labelling')
    notes = algoPitchLabelling(f0,onsets,offsets,fT,samples)

    # post processing
    print('note post-processing')
    algoPostProcessTranscription(notes)

    # write csv file
    writeToCsv(notes,filename[0:len(filename)-3]+'notes.csv')

    # display success & elapsed time
    print('Done!')
    print('Elapsed time: %f seconds' % (time.time()-startTime))

    return

def transcribe(filename, acc = True, f0_file = False, recursive = False,):
    '''
    CANTE: Automatic Note-Level Transcription of Flamenco Singing Recordings.

    Implementation according to:

    [1] Kroher, N. & Gomez, E. (2016). Automatic Transcription of Flamenco Singing from Polyphonic Music Recordings.
    ACM / IEEE Transactions on Audio, Speech and Language Processing, 24(5), pp. 901-913.

    The algorithm creates a .csv file containing the estimated note events corresponding to the
    singing voice melody, where each row corresponds to a note event as follows:

    < note onset [seconds] >, < note duration [seconds] >, < MIDI pitch value >;

    Input is a .wav audio file with a sample rate of 44.1kHz and a bit depth of 16 Bits. Otherwise
    an error is raised.

    If an f0 file is provided, the filename should be identical to the audio file, i.e. for test.wav,
    a file named test.csv should be located in the same folder. The required format matches the output
    of sonic visualizer (www.sonicvisualizer.org) and sonic annotator (http://www.vamp-plugins.org/sonic-annotator/):
    The first column contains the time instants in seconds and the second column holds the corresponding
    pitch values in Hz. Zero or negative pitch values indicate unvoiced frames. Hop size is restricted to
    128 samples for a sample rate of 44.1 kHz.

    In recursive mode, the algorithm transcribes all .wav files in the provided folder path.

    For accompanied recordings (i.e. vocals + guitar), an additional contour filtering stage is
    applied. In this case, set acc = True.

    If you use this code for research purposes, please cite [1].

    :param filename: <string> path to the input file or folder.
    :param acc: <bool> True if accompaniment is expected, False for a cappella recordings.
    :param f0_file: <bool> True if a .csv file containing the fundamental frequency is provided.
    :param recursive: <bool> True for folder recursion.
    :return: NONE - <filename>.notes.csv written to the same folder
    '''

    # transcribe a single file
    if not recursive:
        # sanity check
        if not os.path.isfile(filename):
            print("ERROR: file not found!")
            return
        # transcription
        AST(filename, acc, f0_file)

    # recursive mode
    else:
        # sanity check
        if not os.path.isdir(filename):
            print("ERROR: folder not found!")
            return
        # get list of all wav files
        files = []
        for file in os.listdir(filename):
            if file.endswith(".wav"):
                files.append(file)
        if not filename.endswith('/'):
            filename = filename + '/'
        for file in files:
            AST(filename+file, acc, f0_file)
    return

