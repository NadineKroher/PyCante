from numpy import array, mean, std



def algoPostProcessTranscription(notes):

    '''
    Post-processing stage for automatic note transcription: Notes are transposed or eliminated based on their relative
    pitch and temporal isolation as described in 2-B-III of

    Kroher, N. & Gomez, E. (2016). Automatic Transcription of Flamenco Singing from Polyphonic Music Recordings.
    ACM / IEEE Transactions on Audio, Speech and Language Processing, 24(5), pp. 901-913.

    :param notes: notes: array in which rows correspond to note events; first element -> onset time [seconds], second element
            --> note duration [seconds], third element --> MIDI pitch
    :return: NONE; input array is modified directly
    '''

    # PARAMETERS
    minNoteDurationSec = 0.05
    zScoreTh = 2.5
    temporalOutlierTh = 1.0

    # compute duration mean and std
    noteArray = array(notes)
    pitches = noteArray[:,2]
    mPitch = mean(pitches)
    sPitch = std(pitches)

    for note in notes:
        # remove notes with short duration
        if note[1] < minNoteDurationSec:
            notes.remove(note)
            continue

    for note in notes:
        # remove low pitch outliers
        if (float(note[2])-mPitch)/sPitch < -zScoreTh:
            notes.remove(note)

    # compute duration mean and std
    noteArray = array(notes)
    pitches = noteArray[:,2]
    mPitch = mean(pitches)
    sPitch = std(pitches)

    for note in notes:
        # transpose octave errors
        if (float(note[2])-mPitch)/sPitch > zScoreTh:
            note[2] -= 12

    # remove temporal outliers
    delInds = []
    for i in range(1,len(notes)-1):
        if notes[i][1] > temporalOutlierTh:
            continue
        lastNoteEnd = notes[i-1][0]+notes[i-1][1]
        nextNoteStart = notes[i+1][0]
        if (notes[i][0]-lastNoteEnd) > temporalOutlierTh and (nextNoteStart-(notes[i][0]+notes[i][1])) > temporalOutlierTh:
            delInds.append(i)
    notes = [notes.pop(i) for i in sorted(delInds,reverse=True)]

    return
