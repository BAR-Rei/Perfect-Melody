# coding: utf-8

import numpy as np
import librosa
from scipy.signal import medfilt
from music21 import *

class PitchParser:
    """ Parses the detected pitches and creates a score object. """

    @staticmethod
    def createScore(notes, pulse):
        """ Creates the score from the detected notes and tempo.
            params: 
                notes (list) -> the detected notes, formated by toNote.
                tempo (int) -> the detected tempo
            return: 
                A music21.stream.Score object containing the note with the correct duration, according to tempo.
        """

        # Using the tempo, finds the true note duration
        noteDuration= round(60./(pulse*4.), 1)
        noteLength = 0.25
        durations = {}

        # calculates the duration of each note's type 
        while noteLength <= 4:
            durations[noteLength] = noteDuration
            noteDuration *= 2
            noteLength *= 2

        score = stream.Score()
        score.append(tempo.MetronomeMark(number=pulse))

        # Score creation    
        for i in range(len(notes)):

            noteDuration = round(notes[i]["duration"], 1)
            pitch = notes[i]["pitch"]

            # if the note is too long or too short
            if noteDuration <= durations[0.25]:
                length = 0.25
            elif noteDuration >= durations[4]:
                length = 4

            found = False

            # search in the list the duration of the current note to approximate the duration of this note
            j=0.5
            while found != True and j<=4:
                if noteDuration >= durations[j/2] and noteDuration <= durations[j]:
                    found = True

                    # the duration of the note is approximate to the nearest value
                    if noteDuration - durations[j/2] > durations[j] - noteDuration:
                        length = j
                    else:
                        length = j/2
                j *= 2

            # if the pitch is 1, the note is a silence
            if pitch == -1:
                finalNote = note.Rest()
            else:
                finalNote = note.Note(pitch)

            finalNote.duration.quarterLength = length
            score.append(finalNote)


        return score

    @staticmethod
    def initMeasure(score, measureNumber = 4):
        """ Return the score divided into measures, according to the number of quarter notes by measure.
            params:
                score (stream.Score) -> the initial score
                measureNumber (int) -> the number of quarter notes in a measure
            return:
                the score divided into measures
        """
        measure = stream.Measure()
        result = stream.Score()
        result.append(score.pop(0))


        valueMeasure=0
        for el in score:
            valueNote = el.duration.quarterLength

            while(valueNote != 0):

                # approximation of the duration to an appropriate duration
                value = PitchParser.getCorrectLength(valueNote)
                
                # if the note is too long (upper to the rest of the measure's duration)
                if(valueMeasure + value > measureNumber):
                    valueToAdd = measureNumber - valueMeasure
                    value = valueToAdd

                    # the part necessary to the measure completion is cut from the current value
                    while valueToAdd != 0:

                        length = PitchParser.getCorrectLength(valueToAdd)
                        valueToAdd -= length

                        # note added
                        if el.isNote:
                            noteAdded = note.Note(el.nameWithOctave)
                        elif el.isRest:
                            noteAdded = note.Rest()

                        noteAdded.duration.quarterLength = length
                        measure.append(noteAdded)

                    # end of the measure
                    valueMeasure = measureNumber
                    
                # if the note's duration is lower to the rest of the measure's duration
                else:
                    valueMeasure += value

                    # note added
                    if el.isNote:
                        noteAdded = note.Note(el.nameWithOctave)
                    elif el.isRest:
                        noteAdded = note.Rest()
                    noteAdded.duration.quarterLength = value
                    measure.append(noteAdded)


                # this part of the note had been added
                valueNote -= value

                if valueMeasure == measureNumber:
                    valueMeasure = 0
                    result.append(measure);
                    measure = stream.Measure()


        # Completion of the last measure to add (completed with silences)
        while valueMeasure != measureNumber:
            length = PitchParser.getCorrectLength(measureNumber - valueMeasure)
            silence = note.Rest()

            silence.duration.quarterLength = length
            measure.append(silence)
            valueMeasure += length

        result.append(measure);
            
        return result


    def getCorrectLength(value):
        """ Returns the maximum length possible, considering length supported by the application and the given length.
            params:
                value -> the given length
            return:
                The number of beats the note lasts
        """
        notes_length = [4, 2, 1, 0.5, 0.25]
        i = 0
        while value < notes_length[i]:
            i+=1
        length = notes_length[i]
        return length

    @staticmethod
    def toMidi(pitches):
        """ From a list of detected pitches, returns the midi pitch list, rounded to the closest pitch note.
            params: 
                pitches (numpy.ndarray) -> pitch list
            return: 
                approximate midi note list.
        """
        # determine the nearest note as a midi pitch
        for i in range(len(pitches)):
            element = pitches[i]

            if (element>0):
                pitches[i] = np.round(69 + 12 * np.log2(element/440))

        return pitches



    @staticmethod
    def toNote(midi, sr=22050):
        """ From a midi pitch list, returns the note list, containing tuple (note, duration)
            params: 
                midi (numpy.ndarray) -> midi pitch detected
            return: 
                the note list

            This code has been inspired by audio_to_midi.py, by Justin Salomon.
            link: http://www.justinsalamon.com/news/convert-audio-to-midi-melody-using-melodia
        """
        notes = []
        p_prev = midi[0] if len(midi)>0 else 0
        duration = 0
        onset = 0

        for n, p in enumerate(midi):

            # if the current note is the same as the previous note, 
            # the current note is regrouped with the previous note
            if p==p_prev:
                duration += 1

            # if the current note is different to the previous note
            else:
                duration_sec = duration/float(sr)
                # add note
                onset_sec = onset/float(sr)
                if p_prev == 0:
                    p_prev = -1
                notes.append({"onset": onset_sec, "duration":duration_sec, "pitch":p_prev})

                # start new note
                onset = n
                duration = 1
                p_prev = p


        # add last note
        if p_prev > 0:
            duration_sec = duration/ float(sr)
            onset_sec = onset/ float(sr)
            notes.append({"onset": onset_sec, "duration":duration_sec, "pitch":p_prev})

        return notes


    @staticmethod
    def removeShortNotes(notes,  minDuration=0.1):
        """ Correct all short notes.
            Each short notes is added to the closest note. In the given array, silences are considered as notes with pitch value at -1.
            params:
                notes (list) -> the note list
                minDuration (int) -> the minimum duration of a note
            returns: 
                a list of notes, containing only notes with true durations
        """
        j = 0
        i = 1
        while i<len(notes):
            length = notes[i]["duration"]
            pitch = notes[i]["pitch"]

            # if the notes is too short to be a true note
            if length < minDuration:
                # this note is added to the nearest note
                if i > 0 and i < (len(notes)-1):
                    # if the note is before the current note, it is the last note with a duration > minDuration
                    prevNote = notes[j]
                    nextNote = notes[i+1]
                    
                    # if this notes is circled by two notes at a half-ton difference
                    if prevNote["pitch"] == nextNote["pitch"]:
                        prevNote["duration"] >= minDuration
                        prevNote["duration"] += length
                        prevNote["duration"] += nextNote["duration"]
                        nextNote["duration"] = 0.0
                        i+=1
                    
                    # if not
                    else:
                        if(abs(prevNote["pitch"] - pitch) > abs(nextNote["pitch"] - pitch)):
                            nextNote["duration"]+=length
                        else:
                            prevNote["duration"]+=length

            # if the note has a correct duration
            else:
                # the variable j points to this note
                j = i
            i+=1
        # return the list without the shortest notes. 
        return [el for el in notes if el["duration"] >= minDuration]