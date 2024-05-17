from os import listdir
from os.path import isfile, join
import os
import pdb

folder = "C:\\Users\\spnch\\Documents\\H3B\\data\\jsonFiles\\slot\\dynamic-very-low"
newFolder = "C:\\Users\\spnch\\Documents\\H3B\\data\\jsonFiles\\slot\\64-256-64-inc"

os.rename(join(folder),join(newFolder))
# print(len(tmpLst))
