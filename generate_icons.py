#!/usr/bin/python3
# Programmeringsteknik webbkurs KTH slutinlämning.
# Joel Sjögren
# 2014-08-16
"""
Creates base64 representations of the icons in the command line argument list so that they may be distributed in a single text file icons.txt which looks like
    = name1 =
    ABCDEF0123456789...

    = name2 =
    ABCDEF0123456789...

    = name3 =
    ABCDEF0123456789...
"""

import base64      # encodebytes
import collections # OrderedDict
import os          # path # basename, dirname, exists, join, realpath, splitext
import sys         # argv

# Constants =========================================================
icons_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),\
     "icons.txt")
ex_sep = "\n\n" # Separates icons from icons.
in_sep = "\n"   # Separates icon names from file data.
# Functions =========================================================
def readOldData():
    """Read old icon data that has been created using this script."""
    old_data = collections.OrderedDict() # {category_name: file_data}
    if os.path.exists(icons_filename):
        with open(icons_filename, "r") as old_file:
            old_string = old_file.read()
            if old_string != "":
                for i in old_string.split(ex_sep):
                    category_name, representation = i.split(in_sep, maxsplit=1)
                    old_data[category_name] = representation
    return old_data
def readNewData():
    """Read new icon data, encoding it as base64."""
    new_data = collections.OrderedDict()
    if len(sys.argv) == 1:
        raise Exception("Du gav inga filer som argument!")
    for i in sys.argv[1:]:
        in_file = open(i, "rb")
        in_data = in_file.read()
        if in_data[:4] != bytes("GIF8", "utf-8"):
            raise Exception("`{}' är ingen gif-fil.".format(i))
        representation = base64.encodebytes(in_data).decode().strip("\n")
        filename_without_extension = os.path.splitext(os.path.basename(i))[0]
        category_name = "= {} =".format(filename_without_extension)
        new_data[category_name] = representation
    return new_data
def printDataCategories(message, data):
    """Tell the user what the categories of a set of data are."""
    print(message)
    for i in data:
        print(" ", i)
def combineData(old_data, new_data):
    """Merge two sets of data, overriding the old with the new."""
    result = collections.OrderedDict()
    result.update(old_data)
    result.update(new_data)
    return result
def writeData(out_data):
    """Format the data as a string and write it to disk."""
    out_string = ex_sep.join(i + in_sep + j for i, j in out_data.items())
    out_file = open(icons_filename, "w")
    out_file.write(out_string)
# Main ==============================================================
old_data = readOldData()
printDataCategories("Gamla ikoner:", old_data)
new_data = readNewData()
printDataCategories("Uppdaterar:", new_data)
out_data = combineData(old_data, new_data)
writeData(out_data)
print("Klart!")
