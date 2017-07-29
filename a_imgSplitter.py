# Imports
import pyfits as fits
import numpy as np
from math import floor

# Classes

class Column:
    def __init__(self, name):
        self.name = name
        self.size = 0
        self.data = np.empty
        self.columnSplitter()
        self.col_index = 0
        self.col_data = np.empty
        self.resolution = int(floor(self.size/36))
        self.black = np.median(self.data) * 1.025

    def columnSplitter(self):
        with fits.open(self.name) as x:
            pix_a = x[0]                # pixel array is the first HDUList
            self.data = pix_a.data.T
            self.size = len(self.data)

    def columnSelect(self, index):
        self.col_index = index
        ind_end = index+self.resolution
        self.col_data = self.data[index:ind_end]
