"""
Copyright (C) 2017 Raphael Dawis

This file is part of SoundSpace.

SoundSpace is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""
from astropy.io import fits
import numpy as np
import itertools as it
import os

class Image:
    def __init__(self, image, x_res=36, y_res=36, sensitivity=90):
        """
        Initiates the Image object.

        Takes an image in the FITS format, lowers its resolution to make
        it work with the limited amount of HRIRs in the HRTF folder,
        and normalizes the image such that the column whose lowered resolution
        pixels summed up equal the largest such sum in the image, is set to 1.
        (It's kind of confusing, but basically all the columns take the
        intensity values of all the pixels in their own columns, and the
        largest value you get out of all those is set to 1)

        Parameters:
        ------------
        image : str
            Name of the file you want to open (should be a FITS file for now)
            TO DO: Add other image format support/OpenCV support
        x_res : int
            Amount of pixels across the x dimension. I don't know if I'm
            using it right, but added to attempt to allow for flexible x
            resolution. Make sure this number is the amount of directions
            from left to right you're able to support. (number of hrtfs you
            want to use)
        y_res : int
            Amount of pixels across the y dimension. This *should* be the
            amount of notes you want possible (range of notes) in the image.
        sensitivity : int
            Higher number means less light shows up, max value is 100. This
            is the percentile of light you want to remove.

        (important) Properties:
        ------------
        .name : str
            name of file (for some reason, object name isn't in the headers)
        .chunk_size: int
            x/y resolution of final image
        .reduction : Numpy 2D array, np.float32
            reduced image @ .chunk_size x .chunk_size resolution
        .black : np.float32
            the threshold of the entire image. any number below .black is set to
            0 such that the amplitude for the tone associated with that pixel is
            0.
        """
        self.filename = image

        # If the filename has a bunch of slashes in it, this essentially
        # takes the end of that filename.
        # Example: "/home/user/testimage.fits" -> "testimage"
        self.name = os.path.basename(image).split('.')[0]

        # Opens the image and extracts only the data. No header information
        # is transmitted.
        # The data is transposed such that each column of data is turned into
        # rows which is easier to work with than actual columns spanning rows.
        with fits.open(image) as img:
            self.data = img[0].data.T

        # It's nice to see the data in a log fashion to see more. This is
        # purely for aesthetics and isn't necessary in the transform.
        self.log_data = np.log10(self.data)

        # x_scale * y_scale gives you the resolution of one low-res pixel. This
        # method is pretty nice because you actually can use non-square images
        # and turn them into squares :)
        self.x_res = x_res
        self.y_res = y_res
        self.x_scale = (len(self.data)) / x_res
        self.y_scale = len(self.data[0]) / y_res

        # initiation of the array in which the reduced map will fit
        self.reduction = np.zeros((x_res, y_res))

        # takes the 90th percentile light value in the entire map. anything
        # below this number is set to 0. You can change this number if you
        # want, I just set it to something that looked pretty and did good
        # filtering.
        self.black = np.percentile(self.data, sensitivity)
        self.lower_res()
        self.normalize()

    def lower_res(self, pixel_sens=90):
        """
        Lowers the resolution of the image.

        L o w e r s   t h e   r e s o l u t i o n    o f   t h e   i m a g e.
        This takes a x_scale * y_scale chunk of data and takes the 90th
        percentile of the pixel data. If that happens to be larger than the
        black value, it gets written into the array. If it happens to be
        smaller, the number that goes in is 0.

        Parameters:
        ------------
        pixel_sens : int
            unlike the other sensitivity option, the higher the number here,
            the brighter the pixel will probably be set. Takes the percentile of
            a chunk of data, so the higher the number, the more likely
            something will show up in the representative pixel, and the
            higher value it will be.

        """
        for x, y in it.product(range(self.x_res),
                               range(self.y_res)
                               ):
            self.reduction[x, y] = np.percentile(
                self.data[x * self.x_scale : (x + 1) * self.x_scale,
                          y * self.y_scale: (y + 1) * self.y_scale],
                pixel_sens
            )
            if self.reduction[x, y] < self.black:
                self.reduction[x, y] = 0

    def normalize(self):
        """
        Normalizes the maximum sum of column pixel values to 1.
        This takes the sum of all the columns, puts them into a list,
        picks out the largest sum, then divides the entire 2D array by that
        maximum such that when you add up all the sinewaves in the sound
        array, you get a maximum amplitude of 1, something required to write
        the wav file correctly in a float32 compliant fashion.
        You can change this function to something else if you want like
        logarithmic normalization or something. I don't even know what that
        means yo
        """
        self.reduction /= np.max([np.sum(x) for x in self.reduction])
