# -*- coding:utf-8 -*-
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label 
from kivy.uix.image import Image 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.label import Label

from kivy.properties import *
from kivy.graphics import Color, Ellipse, Line

from kivy.uix.relativelayout import RelativeLayout

from music21 import stream
from math import ceil

""" This module contains all the tools needed to display a score properly
    Graphical instructions are contained in the perfectmelody.kv file. Please take a look at it if this is what you are looking for.
"""

class ScoreWidget(PageLayout):
    """ Displays a complete score. 
        A treble and bass clef are used to display 6 octaves.
        The score can be displayed on multiple pages.

        Contains a list of ScoreLayout, displayed on its different pages
    """

    def __init__(self, **kwargs):
        """ Constructor.
            The _measureWidget attribute contains the MeasureWidgets of the ScoreWidget, in the correct order.
        """
        super().__init__(**kwargs)
        self._measureWidget = []

    def init(self, measureNumber):
        """ Inits the widgets architecure for the next score to display.
            Creates all the pages needed to display the score. Then, initializes the _measureWidget attribute.
            params:
                measureNumber (int) -> number of measures in the score to display
        """
        # Pages creation
        value = int(ceil(measureNumber/4))
        nbPages = value if value>0 else 1
        self.initPages(nbPages)

        # _measureWidget initialisation
        self._measureWidget = []
        for page in self.children:
            for stave in page.children:
                for measure in stave.children:
                    self._measureWidget.append(measure)
                
        self._measureWidget.reverse()

    def initPages(self, nbPages):
        """ Considering a given number of pages, resets the display of all existing needed pages.
            Then, pages are created/removed, depending of the needed number of page for the next score.
        """
        # Reset existing measureWidgets
        for measure in self._measureWidget:
            measure.canvas.after.clear()
            measure.setMeasure(stream.Measure())

        differencePages = nbPages-len(self.children) 

        # Page creation
        if differencePages > 0:
            for i in range(differencePages):
                page = ScoreLayout()
                page.size_hint = (0.8, 1)
                self.add_widget(ScoreLayout())
        # Page removal
        elif differencePages < 0: 
            temp = []
            for i in range(abs(differencePages)):
                temp.append(self.children[len(self.children)-(i+1)])
        
            self.clear_widgets(children=temp)

        print(len(self.children))

    def on_touch_up(self, touch):
        """ This method fixes a kivy bug.
            The parent method is called only if there is more than two score pages.
            params: 
                touch -> the touch event
        """
        if len(self.children)>1:
            super().on_touch_up(touch)


    def displayScore(self, score):
        """ Displays the _score object on the widget.
            params: 
                score -> The score to display
        """
        self.init(len(score[1:]))
        i = 0
        for measure in score[1:]:
            widget = self._measureWidget[i]
            widget.setMeasure(measure)
            i += 1

class ScoreLayout(BoxLayout):
    """ Displays a score page.
        Contains a list of StaveWidget, displayed vertically.    
    """
    pass

class StaveLayout(BoxLayout):
    """ Displays a score stave.
        Contains a list of MeasureWidget, displayed horizontally
    """
    pass



class MeasureWidget(Widget):
    """ Displays a score measure. 
        Displays each note and silence on the measure. Uses a bass and treble clef to display score information.
    """
    #Constants
    NOTES_LETTER = "CDEFGAB"

    START_LINE_TREBLE = 30
    OCTAVES_TREBLE = [4, 5, 6]

    START_LINE_BASS = 130
    OCTAVES_BASS = [1, 2, 3]
    

    LINE_SEPARATION = 10

    NOTES_DIAMETER = 10
    NOTES_WIDTH = 1.1

    NUMBER_LINE = 5 
    START_STEP = 70

    def setMeasure(self, measure):
        """ Sets the measure to display. The measure is saved in the _measure attribute. 
            It updates note positions when the widget size is changed. 
            params: 
                measure (stream.Measure) -> the measure to display
        """
        self._measure = measure
        self.display()
        self.bind(size=self.display, pos=self.display)

    def display(self, *args): 
        """ Displays the _measure attribute on the widget
            params: 
                *args -> graphical instruction sent when the size has changed. Not used in the method.
        """
        # Attributes declaration
        self.step = self.width/5.5

        # Treble Key
        self.firstLineTreble = self.top - (self.START_LINE_TREBLE)
        self.thirdLineTreble = self.top - (self.START_LINE_TREBLE + self.LINE_SEPARATION*2)
        self.fifthLineTreble = self.top - (self.START_LINE_TREBLE + self.LINE_SEPARATION*4)
        self.lowerNoteTreble = self.fifthLineTreble - self.LINE_SEPARATION

        # Bass Key
        self.firstLineBass = self.top - (self.START_LINE_BASS)
        self.thirdLineBass = self.top - (self.START_LINE_BASS + self.LINE_SEPARATION*2)
        self.fifthLineBass = self.top - (self.START_LINE_BASS + self.LINE_SEPARATION*4)
        self.lowerNoteBass = self.fifthLineBass - (self.LINE_SEPARATION*5) - self.LINE_SEPARATION/2

        self.setKey(True)

        self.canvas.after.clear()

        pos_x = self.x + self.START_STEP
        

        ## Notes Positionning
        for note in self._measure:
            x = self.getXPosition(note)
            pos_x += x/2

            length = note.duration.quarterLength

            if note.isNote:
                
                pos_y = self.getYPosition(note)
                
                # Flat/Sharp 
                if "#" in note.name:
                    self.addSharp(pos_x, pos_y)
                elif "-" in note.name:
                    self.addFlat(pos_x, pos_y)

                # Note type
                if length == 1:
                    self.addQuarter(pos_x, pos_y)
                elif length == 2:
                    self.addHalf(pos_x, pos_y)
                elif length == 4:
                    self.addWhole(pos_x, pos_y)
                elif length == 0.5:
                    self.addEighth(pos_x, pos_y)
                elif length == 0.25:
                    self.addSixteenth(pos_x, pos_y)


                # if the missing lines need to be shown
                if pos_y >= self.firstLine or pos_y <= self.fifthLine:
                    self.completeLine(pos_x, pos_y)

            elif note.isRest:

                # Rest type
                if length == 1:
                    self.addCrotchet(pos_x)
                elif length == 0.5:
                    self.addQuaver(pos_x)
                elif length == 0.25:
                    self.addSemiQuaver(pos_x)
                elif length == 2:
                    self.addSemiBreve(pos_x)
                elif length == 4:
                    self.addMinim(pos_x)

            pos_x += x/2

            

    def getXPosition(self, note):
        """ Returns the x coordinate of the note in the measure. 
            params: 
                note (note.Note) -> note to display
        """
        value = note.duration.quarterLength
        return self.step * value


    def getYPosition(self, note):
        """ Returns the y coordinate of the note in the measure. 
            params: 
                note (note.Note) -> note to display
        """
        letter = note.name[0].upper()
        octave = note.octave

        # Bass Key
        if 1 <= octave and octave <= 3:
            octaveStep = self.OCTAVES_BASS.index(note.octave) * self.LINE_SEPARATION/2 * len(self.NOTES_LETTER)
            noteStep = self.NOTES_LETTER.index(letter) * self.LINE_SEPARATION/2
            pos_y = self.lowerNoteBass + noteStep + octaveStep
            self.setKey(False)

        # Treble Key
        else:   
            octaveStep = self.OCTAVES_TREBLE.index(note.octave) * self.LINE_SEPARATION/2 * len(self.NOTES_LETTER)
            noteStep = self.NOTES_LETTER.index(letter) * self.LINE_SEPARATION/2
            pos_y = self.lowerNoteTreble + noteStep + octaveStep
            self.setKey(True)

        return pos_y



    def setKey(self, flag):
        """ Initializes the positionning for the key of the current note, depending of the flag params.
            params: 
                flag (boolean) -> true if it's treble, false otherwise.
        """
        if flag:
            self.firstLine = self.firstLineTreble
            self.thirdLine = self.thirdLineTreble
            self.fifthLine = self.fifthLineTreble
        else:
            self.firstLine = self.firstLineBass
            self.thirdLine = self.thirdLineBass
            self.fifthLine = self.fifthLineBass


    ################### GRAPHICAL INSTRUCTION ###################
    def completeLine(self, pos_x, pos_y):
        """ Displays all the invisible lines separating the notes and the score 
            params: 
                pos_x(int) -> x position of the note
                pos_y(int) -> y position of the note
        """
        if pos_y >= self.firstLine:
            y = self.firstLine-self.LINE_SEPARATION
            while y <= pos_y:
                with self.canvas.after: 
                    Color(0, 0, 0)
                    Line(points=(pos_x - 7, y, pos_x + 7, y), width=self.NOTES_WIDTH)
                y += self.LINE_SEPARATION
        else:
            y = self.fifthLine + self.LINE_SEPARATION
            while y >= pos_y:
                with self.canvas.after: 
                    Color(0, 0, 0)
                    Line(points=(pos_x - 7, y, pos_x + 7, y), width=self.NOTES_WIDTH)
                y -= self.LINE_SEPARATION



    ## Note length
    def addQuarter(self, pos_x, pos_y):
        """ Displays a quarter note at pos_x,pos_y 
            params: pos_x (int) -> the x position of the note
                    pos_y (int) -> the y position of the note
        """
        # if the notes is on the top part of the measure
        if pos_y < self.thirdLine:
            with self.canvas.after:
                Color(0, 0, 0)
                Ellipse(pos=(pos_x - self.NOTES_DIAMETER/2, pos_y - self.NOTES_DIAMETER/2), size=(self.NOTES_DIAMETER, self.NOTES_DIAMETER))
                Line(points=(pos_x + self.NOTES_DIAMETER/2, pos_y, pos_x + self.NOTES_DIAMETER/2, pos_y + 25), width=self.NOTES_WIDTH)
        else:
            with self.canvas.after:
                Color(0, 0, 0)
                Ellipse(pos=(pos_x - self.NOTES_DIAMETER/2, pos_y - self.NOTES_DIAMETER/2), size=(self.NOTES_DIAMETER, self.NOTES_DIAMETER))
                Line(points=(pos_x - self.NOTES_DIAMETER/2, pos_y, pos_x - self.NOTES_DIAMETER/2, pos_y - 25), width=self.NOTES_WIDTH)



    def addEighth(self, pos_x, pos_y):
        """ Displays an eighth note at pos_x,pos_y 
            params: pos_x (int) -> the x position of the note
                    pos_y (int) -> the y position of the note
        """
        # if the notes is on the top part of the measure
        if pos_y < self.thirdLine:
            with self.canvas.after:
                Color(0, 0, 0)
                Ellipse(pos=(pos_x - self.NOTES_DIAMETER/2, pos_y - self.NOTES_DIAMETER / 2), size=(self.NOTES_DIAMETER, self.NOTES_DIAMETER))
                Line(points=(pos_x + self.NOTES_DIAMETER/2, pos_y, pos_x + self.NOTES_DIAMETER/2, pos_y + 25), width=self.NOTES_WIDTH)
                Line(bezier=(pos_x + 5, pos_y + 25, pos_x + 7, pos_y + 20, pos_x + 17, pos_y + 15, pos_x + 10, pos_y + 8), width=self.NOTES_WIDTH)
        else:
            with self.canvas.after:
                Color(0, 0, 0)
                Ellipse(pos=(pos_x - self.NOTES_DIAMETER / 2, pos_y - self.NOTES_DIAMETER / 2), size=(self.NOTES_DIAMETER, self.NOTES_DIAMETER))
                Line(points=(pos_x - self.NOTES_DIAMETER/2, pos_y,pos_x - self.NOTES_DIAMETER/2, pos_y - 25), width=self.NOTES_WIDTH)
                Line(bezier=(pos_x - 5, pos_y - 25, pos_x - 3, pos_y - 20, pos_x + 7, pos_y - 15, pos_x+2, pos_y - 8), width=self.NOTES_WIDTH)

    def addSixteenth(self, pos_x, pos_y):
        """ Displays a sixteenth note at pos_x,pos_y 
            params: pos_x (int) -> the x position of the note
                    pos_y (int) -> the y position of the note
        """
        # if the notes is on the top part of the measure
        if pos_y < self.thirdLine:
            with self.canvas.after:
                Color(0, 0, 0)
                Ellipse(pos=(pos_x - self.NOTES_DIAMETER/2, pos_y - self.NOTES_DIAMETER / 2), size=(self.NOTES_DIAMETER, self.NOTES_DIAMETER))
                Line(points=(pos_x + self.NOTES_DIAMETER/2, pos_y, pos_x + self.NOTES_DIAMETER/2, pos_y + 25), width=self.NOTES_WIDTH)
                Line(bezier=(pos_x + 5, pos_y + 25, pos_x + 7, pos_y + 20, pos_x + 17, pos_y + 15, pos_x + 10, pos_y + 8), width=self.NOTES_WIDTH)
                Line(bezier=(pos_x + 5, pos_y + 18, pos_x + 7, pos_y + 13, pos_x + 17, pos_y + 8, pos_x + 10, pos_y + 1), width=self.NOTES_WIDTH)
        else:
            with self.canvas.after:
                Color(0, 0, 0)
                Ellipse(pos=(pos_x - self.NOTES_DIAMETER / 2, pos_y - self.NOTES_DIAMETER / 2), size=(self.NOTES_DIAMETER, self.NOTES_DIAMETER))
                Line(points=(pos_x - self.NOTES_DIAMETER/2, pos_y,pos_x - self.NOTES_DIAMETER/2, pos_y - 25), width=self.NOTES_WIDTH)
                Line(bezier=(pos_x - 5, pos_y - 25, pos_x - 3, pos_y - 20, pos_x + 7, pos_y - 15, pos_x+2, pos_y - 8), width=self.NOTES_WIDTH)
                Line(bezier=(pos_x - 5, pos_y - 18, pos_x - 3, pos_y - 13, pos_x + 7, pos_y - 8, pos_x+2, pos_y - 1), width=self.NOTES_WIDTH)

    def addHalf(self, pos_x, pos_y):
        """ Displays a half note at pos_x,pos_y 
            params: pos_x (int) -> the x position of the note
                    pos_y (int) -> the y position of the note
        """
        # if the notes is on the top part of the measure
        if pos_y < self.thirdLine:
            with self.canvas.after: 
                Color(0, 0, 0)
                Line(ellipse = (pos_x - self.NOTES_DIAMETER / 2, pos_y - self.NOTES_DIAMETER / 2,  self.NOTES_DIAMETER, self.NOTES_DIAMETER), width=self.NOTES_WIDTH)
                Line(points=(pos_x + self.NOTES_DIAMETER/2, pos_y, pos_x + self.NOTES_DIAMETER/2, pos_y + 25), width=self.NOTES_WIDTH)
        else:
            with self.canvas.after: 
                Color(0, 0, 0)
                Line(ellipse = (pos_x - self.NOTES_DIAMETER / 2, pos_y - self.NOTES_DIAMETER / 2,  self.NOTES_DIAMETER, self.NOTES_DIAMETER), width=self.NOTES_WIDTH)
                Line(points=(pos_x - self.NOTES_DIAMETER/2, pos_y, pos_x - self.NOTES_DIAMETER/2, pos_y - 25), width=self.NOTES_WIDTH)

    def addWhole(self, pos_x, pos_y):
        """ Displays a whole note at pos_x,pos_y 
            params: pos_x (int) -> the x position of the note
                    pos_y (int) -> the y position of the note
        """
        with self.canvas.after:
            Color(0, 0, 0)
            Line(ellipse = (pos_x - self.NOTES_DIAMETER/2, pos_y - self.NOTES_DIAMETER/2,  self.NOTES_DIAMETER, self.NOTES_DIAMETER), width=self.NOTES_WIDTH)



    ## Alteration

    def addSharp(self, pos_x, pos_y):
        """ Adds a sharp transformation beside the note
            params: pos_x (int) -> the x coordinate of the note
                    pos_y (int) -> the y coordinate of the note
        """
        # Changes the positionning just beside the notes
        pos_x = pos_x - 10
        pos_y = pos_y + 6
        with self.canvas.after:
            Color(0,0,0)
            Line(points=(pos_x-2, pos_y-4, pos_x-2, pos_y+4), width=self.NOTES_WIDTH)
            Line(points=(pos_x+2, pos_y-4, pos_x+2, pos_y+4), width=self.NOTES_WIDTH)

            Line(points=(pos_x-4, pos_y-2, pos_x+4, pos_y-2), width=self.NOTES_WIDTH)
            Line(points=(pos_x-4, pos_y+2, pos_x+4, pos_y+2), width=self.NOTES_WIDTH)

    def addFlat(self, pos_x, pos_y):
        """ Adds a flat transformation beside the note
            params: pos_x (int) -> the x coordinate of the note
                    pos_y (int) -> the y coordinate of the note
        """
        # Changes the positionning just beside the notes
        pos_x = pos_x - 10
        pos_y = pos_y + 6
        with self.canvas.after:
             Color(0,0,0)
             Line(points=(pos_x, pos_y-5, pos_x, pos_y+5), width=self.NOTES_WIDTH)
             Line(bezier=(pos_x, pos_y, pos_x+5, pos_y-1, pos_x+6, pos_y-2, pos_x+5, pos_y-3, pos_x, pos_y-4), width=self.NOTES_WIDTH)

    def addNatural(self, pos_x, pos_y):
        """ Adds a natural transformation beside the note
            params: pos_x (int) -> the x coordinate of the note
                    pos_y (int) -> the y coordinate of the note
        """
        # Changes the positionning just beside the notes
        pos_x = pos_x - 10
        pos_y = pos_y + 6
        with self.canvas.after:
            Color(0,0,0)
            Line(points=(pos_x-2, pos_y-4, pos_x-2, pos_y+2), width=self.NOTES_WIDTH)
            Line(points=(pos_x+2, pos_y-2, pos_x+2, pos_y+4), width=self.NOTES_WIDTH)

            Line(points=(pos_x-2, pos_y-2, pos_x+2, pos_y-2), width=self.NOTES_WIDTH)
            Line(points=(pos_x-2, pos_y+2, pos_x+2, pos_y+2), width=self.NOTES_WIDTH)



    ## Silence
    def addSemiBreve(self, pos_x):
        """ Displays a semi breve at pos_x
            params:
                pos_x (int) -> the x position of the rest
        """
        pos_y = self.firstLine+((self.thirdLine-self.firstLine)/2) # second line
        with self.canvas.after:
            Color(0,0,0)
            Line(cap='square', points=[pos_x-4, pos_y-2, pos_x+4, pos_y-2], width=3)


    def addMinim(self, pos_x):
        """ Displays a minim at pos_x
            params:
                pos_x (int) -> the x position of the rest
        """
        pos_y = self.thirdLine  
        with self.canvas.after:
            Color(0,0,0)
            Line(cap='square', points=[pos_x-4, pos_y+2, pos_x+4, pos_y+2], width=3)

    def addCrotchet(self, pos_x):
        """ Displays a Crotchet rest at pos_x
            params: pos_x (int) -> the x position of the rest
        """
        pos_y = self.thirdLine
        with self.canvas.after:
            Color(0, 0, 0)
            Line(joint='bevel', cap='square', points=[pos_x, pos_y+16, pos_x+8, pos_y+8, pos_x, pos_y, pos_x+8, pos_y-8, pos_x-4, pos_y-4, pos_x, pos_y-16], width=1.1)

    def addQuaver(self, pos_x):
        """ Displays a Quaver rest at pos_x
            params: pos_x (int) -> the x position of the rest
        """
        pos_y = self.thirdLine
        with self.canvas.after:
            Color(0, 0, 0)
            Line(ellipse=(pos_x-2, pos_y+3,  4, 4), width=1.5)
            Line(bezier=[pos_x, pos_y+5, pos_x+4, pos_y, pos_x+8, pos_y+5], width=1.1)
            Line(bezier=[pos_x+8, pos_y+5, pos_x+4, pos_y, pos_x+4, pos_y-11], width=1.1)

    def addSemiQuaver(self, pos_x):
        """ Displays a Semi-Quaver rest at pos_x
            params: pos_x (int) -> the x position of the rest
        """
        self.addQuaver(pos_x)
        pos_y = self.thirdLine
        with self.canvas.after:
            Color(0, 0, 0)
            Line(ellipse=(pos_x+1, pos_y+13,  4, 4), width=1.5)
            Line(bezier=[pos_x+3, pos_y+15, pos_x+9, pos_y+11, pos_x+15, pos_y+15], width=1.1)
            Line(bezier=[pos_x+15, pos_y+15, pos_x+9, pos_y+11, pos_x+8, pos_y+5], width=1.1)
