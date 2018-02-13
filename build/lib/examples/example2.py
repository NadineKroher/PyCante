'''
Automatic transcription of an accompanied flamenco singing recording using a given f0 file.
(does not require ESSENTIA)
The fundamental frequency is read from "poly.csv".
'''

import cante

cante.transcribe('poly.wav',acc=True,f0_file=True,recursive=False)