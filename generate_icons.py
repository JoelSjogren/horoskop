#!/usr/bin/python3
# Programmeringsteknik webbkurs KTH kodskelett.
# Joel Sjögren
# 2014-08-11
"""
Creates base64 representations of the icons used so that they may be sent as text files. The result is stored in icons.txt
"""

import base64

categories = ("money", "love", "politics", "knowledge", "age")
outData = []
for i in categories:
    inFile = open("gifs/{}.gif".format(i), "rb")
    inData = inFile.read()
    representation = base64.encodebytes(inData).decode()
    #print(type(representation))
    outData.append(representation)
outFile = open("icons.txt", "w")
outFile.write("\n".join(outData))
