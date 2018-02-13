'''
Automatic transcription of an accompanied flamenco singing recording from the raw audio file.
(requires ESSENTIA)
'''

import cante

cante.transcribe('poly.wav',acc=True,f0_file=False,recursive=False)

