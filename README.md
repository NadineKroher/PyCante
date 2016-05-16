cante
=====

A python package for automatic transcription of flamenco singing.

CANTE estimates a note-level transcription from an accompanied or acappella flamenco singing recording.


Requirements
------------

CANTE depends on numpy/scipy (https://www.scipy.org).

Melody extraction uses the MELODIA (http://www.justinsalamon.com/melody-extraction.html) algorithm and requires the
essentia (http://essentia.upf.edu) python bindings. If you wish to use a different pitch tracker you can provide a
.csv file as input instead.


Installation
------------

Download the latest distribution from 

    http://tinyurl.com/z4d44ea

unpack and run 
    
    python setup.py install
    
or alternatively clone this directory

    git clone https://github.com/NadineKroher/PyCante
    

Usage
-----
    import cante

    python cante.transcribe(filename, acc=True, f0_file=False, recursive=False)

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

    :param filename: <string> path to the input file or folder.
    :param acc: <bool> True if accompaniment is expected, False for a cappella recordings.
    :param f0_file: <bool> True if a .csv file containing the fundamental frequency is provided.
    :param recursive: <bool> True for folder recursion.
    :return: NONE - <filename>.notes.csv written to the same folder

Three basic use cases are provided in the ./examples folder.


Citing
------

Please cite the following publication if you use this code for reasearch purposes:

    Kroher, N. & Gomez, E. (2016). Automatic Transcription of Flamenco Singing from Polyphonic Music Recordings.
    ACM / IEEE Transactions on Audio, Speech and Language Processing, 24(5), pp. 901-913.


Contact
-------

For feedback or inquiries, please contact: nkroher at us dot es
