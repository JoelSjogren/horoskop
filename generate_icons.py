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
import os          # path # basename, dirname, exists, join, splitext
import sys         # argv

# Constants =========================================================
iconsFilename = os.path.join(os.path.dirname(__file__), "icons.txt")
exSep = "\n\n" # Separates icons from icons.
inSep = "\n"   # Separates icon names from file data.
# Functions =========================================================
def readOldData():
    """Read old icon data that has been created using this script."""
    oldData = collections.OrderedDict() # {categoryName: fileData}
    if os.path.exists(iconsFilename):
        with open(iconsFilename, "r") as oldFile:
            oldString = oldFile.read()
            if oldString != "":
                for i in oldString.split(exSep):
                    categoryName, representation = i.split(inSep, maxsplit=1)
                    oldData[categoryName] = representation
    return oldData
def readNewData():
    """Read new icon data, encoding it as base64."""
    newData = collections.OrderedDict()
    if len(sys.argv) == 1:
        raise Exception("Du gav inga filer som argument!")
    for i in sys.argv[1:]:
        inFile = open(i, "rb")
        inData = inFile.read()
        if inData[:4] != bytes("GIF8", "utf-8"):
            raise Exception("`{}' är ingen gif-fil.".format(i))
        representation = base64.encodebytes(inData).decode().strip("\n")
        categoryName = "= {} =".format(os.path.splitext(os.path.basename(i))[0])
        newData[categoryName] = representation
    return newData
def printDataCategories(message, data):
    """Tell the user what the categories of a set of data are."""
    print(message)
    for i in data:
        print(" ", i)
def combineData(oldData, newData):
    """Merge two sets of data, overriding the old with the new."""
    result = collections.OrderedDict()
    result.update(oldData)
    result.update(newData)
    return result
def writeData(outData):
    """Format the data as a string and write it to disk."""
    outString = exSep.join(i + inSep + j for i, j in outData.items())
    outFile = open(iconsFilename, "w")
    outFile.write(outString)
# Main ==============================================================
oldData = readOldData()
printDataCategories("Gamla ikoner:", oldData)
newData = readNewData()
printDataCategories("Uppdaterar:", newData)
outData = combineData(oldData, newData)
writeData(outData)
print("Klart!")
