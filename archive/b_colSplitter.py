# Imports
from math import floor
import numpy as np

# Globals

# Functions
class Pixel:
    def __init__(self, col_data, black):
        self.black = black
        self.column = col_data
        self.size = len(col_data[0])
        self.resolution = int(floor(self.size/36))
        self.adjust = np.empty((1,0), int)

    def resShift(self):
        for index in range(0, self.size-self.resolution, self.resolution):
            new_pixel = np.percentile(self.column[:,
                                      index:index+self.resolution], 90)
            if new_pixel < self.black:
                new_pixel = 0
            else:
                pass
            self.adjust = np.append(self.adjust, new_pixel)
