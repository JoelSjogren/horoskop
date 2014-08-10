#!/usr/bin/python3
# Programmeringsteknik webbkurs KTH kodskelett.
# Joel Sjögren
# 2014-08-08
"""
Tells the user what his life will be like.

Of course the prediction may not be correct, but at least the result is well defined by the user's date of birth and three files containing prediction data. Some predictions are predefined as a whole (in pred-whole.txt); others are composed by properties and consequences (in pred-prop.txt and pred-conseq.txt).

To make a prediction, the user's birthdate will do. We don't need a User class to contain that information. There's no need to overdo extensibility in a small application. Likewise, we don't need a Prediction class. However, I have decided that the algorithm used to make predictions should be exchangeable because there are several potential algorithms in the field of astrology. The question is whether the common interface for making predictions should be just a function or a class. I have chosen to make a class, namely Predictor, because that way resources (in this case, the three files) need to be opened only once instead of each time a prediction is made.

I plan on having two user interfaces: a gui by default and a cli as fallback. Because they will contain the main loop, they will have big enough scope without having to be objects, so I made them functions.

Here goes a general note about my naming convention. Variables look like_this, functions likeThis and classes LikeThis. Constants don't get any special treatment. Moreover, if a variable ends with an s denoting plural (chairs) the variable is a list. If it ends with a c (chairc) it holds the count of something. For example,
    >>> materials = ["straw", "wood", "bricks"]
    >>> materialc = 3
"""

import datetime
import sys
import time
import tkinter, tkinter.ttk
import traceback

class Predictor:
    """Creates predictions based on dates."""
    def __init__(self):
        # The data attributes hold strings that are part of predictions.
        # data_whole contains whole sentences arranged by category.
        # data_prop contains properties arranged by age group.
        # data_prop contains possible consequences of the properties above.
        self.data_whole = [[], [], []] # [Money, Love, Politics]
        self.data_prop = [[], [], []] # [Infant, Young, Grown-up]
        self.data_conseq = [[], [], []] # [Infant, Young, Grown-up]
        self.readData()
    def readData(self):
        """Fill the data attributes by reading from files."""
        def readIntoLists(lists, filename):
            """Read lines into lists, moving to the next list on empty line."""
            category = 0
            with open(filename) as whole:
                for i in whole.read().splitlines():
                    if i == "":
                        category += 1
                    else:
                        lists[category].append(i)
        readIntoLists(self.data_whole, "pred-whole.txt")
        readIntoLists(self.data_prop, "pred-prop.txt")
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
def cli():
    """Interact with the user on the command line."""
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
    tell("...\n", delay=0.4, pause=False)
    date = askDate("När är du född?")
    pred = Predictor().predict(date)
    tellPrediction(pred)
    input("Tryck ENTER för att avsluta.")
def gui():
    from tkinter import Listbox, END, X, Tk, messagebox
    from tkinter.ttk import Label, Entry, Button, Frame
    """Interact with the user graphically."""
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
        def setListener(self, predView):
            self.predView = predView
        def onDateChanged(self):
            """Notifies the PredictionWidget that the date has been changed."""
            try:
                date = datetime.datetime.strptime(self.entry.get(),
                     "%Y-%m-%d").date()
                self.predView.refresh(date)
            except ValueError:
                pass
    class PredictionWidget(Frame):
        """Shows a prediction to the user."""
        def __init__(self, master):
            Frame.__init__(self, master)
            self.box = Listbox(master)
            self.box.pack(fill=X)
            self.predictor = Predictor()
        def refresh(self, date):
            """Set the prediction based on the user's input."""
            self.box.delete(0, END)
            for i in self.predictor.predict(date):
                self.box.insert(END, i)
    class MainWindow(Tk):
        """Represents the window with core functionality."""
        def __init__(self, *args, **kwargs):
            """Make boxes, register callbacks etc."""
            Tk.__init__(self, *args, **kwargs)
            self.wm_title("Horoskop")
            self.geometry("500x320")
            date = DateWidget(self)
            date.pack(pady=10)
            pred = PredictionWidget(self)
            pred.pack()
            date.setListener(pred)
        def report_callback_exception(self, *args):
            """If exception raised, don't just fail silently. Overrides."""
            Tk.report_callback_exception(self, *args)
            messagebox.showerror("Ett fel har uppstått", "För mer information,"
                + " kör programmet från en terminal eller kommandotolk."
                + " Programmet kommer nu att avslutas.")
            sys.exit(1)
    mainWindow = MainWindow()
    mainWindow.mainloop()
try:
    gui()
except tkinter.TclError:
    cli()






