'''
Automatic transcription of an a cappella flamenco singing recording from the raw audio file.
(requires ESSENTIA)
'''

import cante

cante.transcribe('acappella.wav',acc=True,f0_file=False,recursive=False)