#!/usr/bin/python3
# Programmeringsteknik webbkurs KTH kodskelett.
# Joel Sjögren
# 2014-08-13
"""
Tells the user what his life will be like.

Of course the prediction may not be correct, but at least the result is well defined by the user's date of birth and three files containing prediction data. Some predictions are predefined as a whole (in pred-whole.txt); others are composed by properties and consequences (in pred-prop.txt and pred-conseq.txt).

To make a prediction, the user's birthdate will do. We don't need a User class to contain that information. There's no need to overdo extensibility in a small application. Likewise, we don't need a Prediction class. However, I have decided that the algorithm used to make predictions should be exchangeable because there are several potential algorithms in the field of astrology. The question is whether the common interface for making predictions should be just a function or a class. I have chosen to make a class, namely Predictor, because that way resources (in this case, the three files) need to be opened only once instead of each time a prediction is made.

I plan on having two user interfaces: a gui by default and a cli as fallback. Because they will contain the main loop, they will have big enough scope without having to be objects, so I made them functions.

Here goes a general note about my naming convention. Variables look like_this, functions likeThis and classes LikeThis. Constants don't get any special treatment. Moreover, if a variable ends with an s denoting plural (chairs) the variable is a list. If it ends with a c (chairc) it holds the count of something. For example,
    >>> materials = ["straw", "wood", "bricks"]
    >>> materialc = 3
"""

import datetime     # date, datetime.strptime (parses date)
import math         # cos, pi, sin
import sys          # exit, stdout.flush
import textwrap     # fill (wraps text)
import time         # sleep
import tkinter      # some widgets and data classes and constants
import tkinter.ttk  # some widgets

# Classes ===========================================================
class Predictor:
    """Creates predictions based on dates."""
    def __init__(self):
        # The data attributes hold strings that are part of predictions.
        # data_whole contains whole sentences arranged by category.
        # data_prop contains properties arranged by age group.
        # data_prop contains possible consequences of the properties above.
        self.data_whole = [[], [], [], []] # [Money, Love, Politics, Knowledge]
        self.data_prop = [[], [], []]      # [Infant, Young, Grown-up]
        self.data_conseq = [[], [], []]    # [Infant, Young, Grown-up]
        self.readData()
    def readData(self):
        """Fill the data attributes by reading from files."""
        def readIntoLists(lists, filename):
            """Read lines into lists, moving to the next list on empty line."""
            category = 0
            with open(filename, "rb") as whole:
                for i in whole.read().decode("utf-8").splitlines():
                    if i == "":
                        category += 1
                    else:
                        lists[category].append(i)
        readIntoLists(self.data_whole,  "pred-whole.txt")
        readIntoLists(self.data_prop,   "pred-prop.txt")
        readIntoLists(self.data_conseq, "pred-conseq.txt")
    def ageGroup(self, date):
        """Determine the age group of a person born on the date: 0, 1 or 2."""
        age = datetime.date.today() - date
        if age.days < 400:
            return 0
        if age.days < 10000:
            return 1
        return 2
    def index(self, date):
        """Determine an index to be used as a kind of random seed."""
        return date.toordinal()
    def composePrediction(self, date):
        """Make a prediction by combining data_prop and data_conseq."""
        ageGroup = self.ageGroup(date)
        index = self.index(date)
        propAndConseq = [None, None]
        for i, j in ((0, self.data_prop), (1, self.data_conseq)):
            chooseFrom = j[ageGroup]
            propAndConseq[i] = chooseFrom[index % len(chooseFrom)]
        return "Din {} förorsakar {}.".format(*propAndConseq)
    def predict(self, date):
        """Make a prediction."""
        index = self.index(date)
        result = []
        for i in self.data_whole:
            result.append(i[index % len(i)])
        result.append(self.composePrediction(date))
        return result
# Functions =========================================================
def cli():
    """Interact with the user on the command line."""
    # Functions =====================================================
    def tell(*args, delay=0.03, pause=True):
        """Print one letter at a time and pause at the end by default."""
        msg = " ".join(str(i) for i in args)
        for i in msg:
            print(i, end="")
            sys.stdout.flush()
            time.sleep(delay)
        if pause:
            input()
    def askDate(question):
        """Ask the user for a date."""
        tell(question + " [ÅÅÅÅ-MM-DD] ", pause=False)
        while True:
            try:
                return datetime.datetime.strptime(input(), "%Y-%m-%d").date()
            except ValueError:
                tell("Hursa? ", pause=False)
    def tellPrediction(pred):
        """Reveal the prediction to the user."""
        for i in pred:
            tell(" - ", delay=0, pause=False)
            tell(i)
    # Main ==========================================================
    tell("...\n", delay=0.4, pause=False)
    date = askDate("När är du född?")
    pred = Predictor().predict(date)
    tellPrediction(pred)
    input("Tryck ENTER för att avsluta.")
def gui():
    """Interact with the user graphically."""
    from tkinter import BOTH, CENTER, DISABLED, END, FLAT, IntVar, Listbox, \
         messagebox, NORMAL, PhotoImage, Radiobutton, Text, Tk, WORD, X
    from tkinter.ttk import Label, Entry, Button, Frame, Style
    # Classes =======================================================
    class DateWidget(Frame):
        """Gets a date from the user."""
        def __init__(self, master):
            Frame.__init__(self, master)
            self.label = Label(self, text="När är du född?")
            self.label.pack()
            self.entry = Entry(self, width=12)
            self.entry.insert(0, "ÅÅÅÅ-MM-DD")
            self.entry.pack(pady=5)
            self.button = Button(self, text="Uppdatera",
                 command=lambda: self.onDateChanged())
            self.button.pack()
            self.entry.focus_set()
            self.entry.select_range(0, END)
            self.entry.bind("<Return>", lambda x: self.onDateChanged())
        def setListener(self, predView):
            self.predView = predView
        def onDateChanged(self):
            """Notifies the PredictionWidget that the date has been changed."""
            try:
                date = datetime.datetime.strptime(self.entry.get(),
                     "%Y-%m-%d").date()
                self.predView.update(date)
            except ValueError:
                pass
    class PredictionWidget(Frame):
        """Shows a prediction to the user."""
        def __init__(self, master):
            Frame.__init__(self, master)
            self.text = Label(self, justify=CENTER, font="Arial 14", background="grey")
            self.predictor = Predictor()
            self.categories = []
            self.bind("<Configure>", self.onResize)
            self.activeCategory = IntVar()
            self.date = None
            for i in self.getIcons():
                category = Radiobutton(self, image=i,
                     variable=self.activeCategory, value=len(self.categories),
                     indicatoron=False, width=64, height=64,
                     command=self.update)
                category.imageData = i
                self.categories.append(category)
        def getIcons(self):
            result = []
            representations = open("icons.txt").read().split("\n\n")
            for i in representations:
                image = PhotoImage(data=i)
                result.append(image)
            return result
        def placeCenterOf(self, widget, pos):
            widget.place(anchor="center", x=pos[0],y=pos[1])
        def onResize(self, event):
            """Rearrange the children when geometry of self changes."""
            if event.widget == self:
                center = (event.width / 2, event.height / 2)
                radius = min(center) - 32 # todo meaningless literal
                self.text.place(anchor=CENTER, x=center[0], y=center[1])
                for i, j in enumerate(self.categories):
                    turn = 2 * math.pi
                    angle = turn * (1 / 4 - i / len(self.categories))
                    j.place(anchor=CENTER,
                            x=center[0] + math.cos(angle) * radius,
                            y=center[1] - math.sin(angle) * radius)
        def update(self, date=None):
            """Change contents based on circumstances. Set date if given."""
            if date:
                self.date = date
            if self.date:
                predictions = self.predictor.predict(self.date)
                prediction = predictions[self.activeCategory.get()]
                prediction = textwrap.fill(prediction, width=20) # todo lit dup
            else:
                prediction = ""
            self.text.configure(text=prediction)
    class MainWindow(Tk):
        """Represents the window with core functionality."""
        def __init__(self, *args, **kwargs):
            """Make boxes, register callbacks etc."""
            Tk.__init__(self, *args, **kwargs)
            self.wm_title("Horoskop")
            self.geometry("500x500")
            self.resizable(False, False)
            date = DateWidget(self)
            date.pack(pady=10)
            pred = PredictionWidget(self)
            pred.pack(fill=BOTH, expand=True, padx=20, pady=20)
            date.setListener(pred)
        def report_callback_exception(self, *args):
            """If exception raised, don't just fail silently. Overrides."""
            Tk.report_callback_exception(self, *args)
            messagebox.showerror("Ett fel har uppstått", "För mer information,"
                 + " kör programmet från en terminal eller kommandotolk."
                 + " Programmet kommer nu att avslutas.")
            sys.exit(1)
    # Main ==========================================================
    mainWindow = MainWindow()
    mainWindow.mainloop()
def hasDisplay():
    """Determines whether the gui will work."""
    try:
        tkinter.Tk().destroy()
    except:
        return False
    return True
# Main ==============================================================
if hasDisplay():
    gui()
else:
    cli()
"""
Todo before submitting prototype:
 - Add comments.
Todo after submitting prototype::
 - Make categories dynamic. Not just five should be allowed.
    + Revise the structure of Predictor.data_whole.
    + Revise the structure of data_whole.txt.
 - Always hide either user input or output?
 - Tell the user if the date entered is malformed.
"""



