#!/usr/bin/python3
# Programmeringsteknik webbkurs KTH slutinlämning.
# Joel Sjögren
# 2014-08-16
"""
Tells the user what his life will be like.

Of course the prediction may not be correct, but at least the result is well defined by the user's date of birth and three files containing prediction data. Some predictions are predefined as a whole (in pred-whole.txt); others are composed by properties and consequences (in pred-prop.txt and pred-conseq.txt).

To make a prediction, the user's birthdate will do. We don't need a User class to contain that information. There's no need to overdo extensibility in a small application. Likewise, we don't need a Prediction class. However, I have decided that the algorithm used to make predictions should be exchangeable because there are several potential algorithms in the field of astrology. The question is whether the common interface for making predictions should be just a function or a class. I have chosen to make a class, namely Predictor, because that way resources (in this case, the three files) need to be opened only once instead of each time a prediction is made.

There are two user interfaces: a gui by default and a cli as fallback. Because they contain the main part of the program, they will have big enough scope without having to be objects, so I made them functions.

The gui icons are gif images stored as base64 text in icons.txt. To add new gif icons or replace existing ones, run generate_icons.py with the filenames as arguments. The internal name of the icon is the name of the gif minus the extension with "= " and " =" added around it. For example, "foo.gif" becomes "= foo =". All icons must be 64x64 pixels large at the moment.

Here goes a general note about my naming convention. Variables look like_this, functions likeThis and classes LikeThis. Constants don't get any special treatment. Moreover, if a variable ends with an s denoting plural (chairs) the variable is a list. If it ends with a c (chairc) it holds the count of something. For example,
    >>> materials = ["straw", "wood", "bricks"]
    >>> materialc = 3
"""

import collections  # OrderedDict
import datetime     # date, datetime.strptime (parses date)
import math         # cos, pi, sin
import os           # path.dirname, path.join, path.realpath
import sys          # exit, stdout.flush
import textwrap     # fill (wraps text)
import time         # sleep
import tkinter      # some widgets and data classes and constants
import tkinter.ttk  # some widgets
import traceback    # print_exc

# Classes ===========================================================
class Predictor:
    """Creates predictions based on dates."""
    def __init__(self):
        # The data attributes hold strings that are part of predictions.
        # data_whole contains whole sentences arranged by category.
        # data_prop contains properties arranged by age group.
        # data_prop contains possible consequences of the properties above.
        # The data is structured as {categoryName: strings}.
        self.data_whole = collections.OrderedDict()  # Categories: money, etc.
        self.data_prop = collections.OrderedDict()   # Categories: child, etc.
        self.data_conseq = collections.OrderedDict() # Categories: child, etc.
        self.readData()
    def readData(self):
        """Fill the data attributes by reading from files."""
        def readToCategories(categories, filename):
            """Read named groups of lines into a dictionary."""
            with open(filename, "rb") as whole:
                groups = whole.read().decode("utf-8").replace("\r\n", "\n").\
                     replace("\r", "\n").strip("\n").split("\n\n")
                for group in groups:
                    name, lines = (lambda x: (x[0], x[1:]))(group.split("\n"))
                    categories[name] = lines
        readToCategories(self.data_whole,  nextToThisFile("pred-whole.txt"))
        readToCategories(self.data_prop,   nextToThisFile("pred-prop.txt"))
        readToCategories(self.data_conseq, nextToThisFile("pred-conseq.txt"))
    def ageGroup(self, date):
        """Determine the age group of a person born on the date."""
        age = datetime.date.today() - date
        if age.days < 5000:
            return "= child ="
        if age.days < 10000:
            return "= young ="
        return "= senior ="
    def index(self, date):
        """Determine an index to be used as a kind of random seed."""
        return date.toordinal()
    def chooseFromWholePredictions(self, date):
        """Like self.predict but using only self.data_whole as a source."""
        result = collections.OrderedDict()
        index = self.index(date)
        for i, j in self.data_whole.items():
            result[i] = j[index % len(j)]
        return result
    def composePrediction(self, date):
        """Make a prediction by combining data_prop and data_conseq."""
        age_group = self.ageGroup(date)
        index = self.index(date)
        prop_and_conseq = [None, None]
        for i, j in ((0, self.data_prop), (1, self.data_conseq)):
            choose_from = j[age_group]
            prop_and_conseq[i] = choose_from[index % len(choose_from)]
        return "Din {} förorsakar {}.".format(*prop_and_conseq)
    def predict(self, date):
        """Make a full set of predictions {category_name: prediction}."""
        result = self.chooseFromWholePredictions(date)
        result["= age ="] = self.composePrediction(date)
        return result
    def categories(self):
        """Make a list of names of known categories."""
        return list(self.data_whole) + ["= age ="]
# Functions =========================================================
def nextToThisFile(filename):
    """Join the directory in which this program resides with the filename."""
    directory = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(directory, filename)
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
        for i in pred.values():
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
    from tkinter import BOTH, CENTER, END, \
         messagebox, PhotoImage, Radiobutton, StringVar, Tk
    from tkinter.ttk import Label, Entry, Button, Frame, Style
    # Constants =====================================================
    window_width = 500
    window_height = 500
    date_entry_width = 12
    prediction_text_width = 20
    small_pad = 5
    medium_pad = 10
    big_pad = 20
    icon_size = 64
    # Classes =======================================================
    class DateWidget(Frame):
        """Gets a date from the user."""
        def __init__(self, master):
            """Make boxes, register callbacks etc."""
            Frame.__init__(self, master)
            self.label = Label(self, text="När är du född?")
            self.label.pack()
            self.entry_text = StringVar()
            self.entry_text.trace("w", lambda *args: self.onEntryChanged())
            self.entry = Entry(self, width=date_entry_width,
                 textvariable=self.entry_text)
            self.entry.insert(0, "ÅÅÅÅ-MM-DD")
            self.entry.pack(pady=small_pad)
            self.button = Button(self, text="Uppdatera",
                 command=lambda: self.onDateChanged())
            self.button.pack()
            self.entry.focus_set()
            self.entry.select_range(0, END)
            self.entry.bind("<Return>", lambda x: self.onDateChanged())
        def setListener(self, pred_view):
            """Select whom to notify when a new date is entered."""
            self.pred_view = pred_view
        def onDateChanged(self):
            """Notifies the PredictionWidget that the date has been changed."""
            try:
                date = datetime.datetime.strptime(self.entry.get(),
                     "%Y-%m-%d").date()
                self.pred_view.update(date)
            except ValueError:
                self.entry.configure(foreground="red")
        def onEntryChanged(self):
            """Reset the text color."""
            self.entry.configure(foreground="")
    class PredictionWidget(Frame):
        """Shows a prediction to the user."""
        def __init__(self, master):
            """Make boxes, register callbacks etc."""
            Frame.__init__(self, master)
            self.active_category = StringVar()
            self.bind("<Configure>", self.onResize)
            self.date = None
            self.predictor = Predictor()
            self.category_buttons = self.createCategoryButtons()
            self.text = Label(self, justify=CENTER, font="Arial 14")
        def createCategoryButtons(self):
            """Create the buttons used to choose category. Return them."""
            result = []
            icons = self.readIcons()
            categories = self.predictor.categories()
            for i in categories:
                if i in icons:
                    icon = icons[i]
                else:
                    icon = icons["= default ="]
                category_button = Radiobutton(self, image=icon,
                     variable=self.active_category, value=i, indicatoron=False,
                     width=icon_size, height=icon_size, command=self.update)
                category_button.image_data = icon
                result.append(category_button)
            self.active_category.set(categories[0])
            return result
        def readIcons(self):
            """Read the gui icons from disk. Return them."""
            result = {}
            categories = open(nextToThisFile("icons.txt")).read().split("\n\n")
            for i in categories:
                category_name, file_data = i.split("\n", maxsplit=1)
                image = PhotoImage(data=file_data)
                result[category_name] = image
            return result
        def onResize(self, event):
            """Rearrange the children when the geometry of self changes."""
            if event.widget == self:
                center = (event.width / 2, event.height / 2)
                radius = min(center) - icon_size / 2
                self.text.place(anchor=CENTER, x=center[0], y=center[1])
                for i, j in enumerate(self.category_buttons):
                    turn = 2 * math.pi
                    angle = turn * (1 / 4 - i / len(self.category_buttons))
                    j.place(anchor=CENTER,
                            x=center[0] + math.cos(angle) * radius,
                            y=center[1] - math.sin(angle) * radius)
        def update(self, date=None):
            """Change contents based on circumstances. Set date if given."""
            if date:
                self.date = date
            if self.date:
                predictions = self.predictor.predict(self.date)
                prediction = predictions[self.active_category.get()]
                prediction = textwrap.fill(prediction, width=20)
            else:
                prediction = ""
            self.text.configure(text=prediction)
    class MainWindow(Tk):
        """Represents the main window with core functionality."""
        def __init__(self, *args, **kwargs):
            """Make boxes, register callbacks etc."""
            Tk.__init__(self, *args, **kwargs)
            self.wm_title("Horoskop")
            self.geometry("{}x{}".format(window_width, window_height))
            self.minsize(window_width, window_height)
            self.date = DateWidget(self)
            self.date.pack(pady=medium_pad)
            self.pred = PredictionWidget(self)
            self.pred.pack(fill=BOTH, expand=True, padx=big_pad, pady=big_pad)
            self.date.setListener(self.pred)
        def report_callback_exception(self, *args):
            """If exception raised, don't just fail silently. Overrides."""
            Tk.report_callback_exception(self, *args)
            tellTerminate()
    # Functions =====================================================
    def tellTerminate():
        """Tell the user that something went wrong, then exit."""
        messagebox.showerror("Ett fel har uppstått", "För mer information,"
             + " kör programmet från en terminal eller kommandotolk."
             + " Programmet kommer nu att avslutas.")
        sys.exit(1)
    def tellWelcome():
        """Welcome the user."""
        messagebox.showinfo("Välkommen!", "Ditt öde bestäms nu.")
    # Main ==========================================================
    try:
        main_window = MainWindow()
        main_window.update()
        tellWelcome()
        main_window.mainloop()
    except:
        traceback.print_exc()
        tellTerminate()
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
