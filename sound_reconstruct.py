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
import numpy as np
import scipy.io.wavfile as sp
import os
class SoundSpace:

    def __init__(self, volume_list, notetime, y_res=36, spacing=12):
        """
        Initializes the SoundSpace object.

        Starts an object that converts all the sounds

        Parameters:
        ------------
        volume_list : Numpy 2d array in np.float32
            Contains a matrix of data relating to pixel intensity
        notetime : float
            Basically the duration of the chord you want played (in seconds)
        y_res : int
            How many notes you want sequentially (defaults to 36 notes)
        spacing : int -> np.float32
            How far apart you want the notes (defaults to half steps;
            see comments about common chromatic tunings) (uses A2 = 110 Hz)

        (important) Properties:
        ------------
        .notes : list, int
            list of frequencies. You can change this to whatever values you
            want, I have it set to half step intervals from A2 to almost A5 I
            think. There are currently 36 notes; if you add more, change
            y_res in img_deconstruct. I should have a settings file tbh
        .framerate : int
            it's actually the sample rate, default is 44100, but 48000 is like
            studio quality (if you're really worried about harmonics aliasing,
            just use some arbitrarily high number BUT BE WARNED that it takes
            more effort to use a higher frame rate. The computer I'm using
            sometimes doesn't like running my program because it takes up too
            much memory.)
        .x_spc : Numpy array, np.float32
            The range between 0 -> 2pi * duration, sampled .framect times.
            Follows the sample rate*duration to find .framect
        .sineGenArray : list, Numpy arrays, np.float32
            All the sine waves for each note in each pixel position across
            all the rows. Makes sense in monoSigGen.
        """

        # I got clever and just used the formula for generating half stepped
        # note frequencies for notes, starting at 110 Hz (A2 or something.)
        # You can adjust the parameter for how many notes you want
        # encompassed by the map by setting y_res when calling this object
        # (defaults to 36).
        # If you really want to change the tuning spacing, change the spacing
        # variable to something else.
        # spacing = 24 -> .25 steps (harder to distinguish unless multiple
        #                            playing at once)
        # spacing = 12 -> .5 steps (minor 2nds)
        # spacing = 6 -> 1.0 steps (major 2nds)
        # spacing = 4 -> 1.5 steps (minor 3rds)
        # spacing = 3 -> 2.0 steps (major 3rds)
        # spacing = 2 -> 2.5 steps (perfect 4ths)
        self.notes = [110. * (2 ** (n/np.float32(spacing)))
                      for n in range(y_res)]

        self.framerate = 44100
        self.notetime = notetime
        self.framect = int(self.framerate*self.notetime)
        self.volumes = volume_list
        self.x_spc = np.linspace(0, 2*np.pi*self.notetime, self.framect)

        # How to interpret sineGenArray:
        # 1) We'll take all the note frequencies in self.notes.
        # 2) multiply each note into x_spc to get the list of numbers we'll
        #    be taking the sine, meaning we have an np.float32 array for one
        #    frequency in the range 0->2pi*duration. If you graph this,
        #    it's literally just a straight line with a slope
        # 3) Take the sine of that array we just made to make the cool
        #    oscillating graph that you associate with sine.
        # 4) Rinse/repeat for the remaining 35 notes, and store them all in
        #    this neat list.
        # You might be asking "wtf why do i need this", and the answer is
        # really just repeated processing using the array. Having it stored
        # in memory is nice, but I suppose you should technically trash it
        # after you use it.
        self.sineGenArray = [np.sin(note * self.x_spc) for note in self.notes]
        self.mono_sig = self.monoSigGen()
        self.stereo_sig = self.stereoSigGen()

    def monoSigGen(self):
        """
        Makes the mono signals for use with the stereo signal.

        Transforms the sineGenArray by dot multiplying in each of the volumes to
        each pixel's assigned sine wave.

        Return:
        ------------
        tmp : list, Numpy array, np.float32
            all the volumes are applied and adds click/ding track in there too.
            please note that click/ding might need to be changed to a voice
            saying a word like "one" "five" "ten" or something.
        """
        tmp = []

        # This is just doing element-wise multiplication in array.
        # As an example: np.dot([1, 2, 3, 4], [5, 4, 3, 2]) => [5, 8, 9, 8]
        # They call it dot multiplication in NumPy.
        # This adjusts the volume appropriately for each frequency in a
        # column. It does this for all the columns.
        for c_vol in range(len(self.volumes)):
            a1 = np.dot(self.volumes[c_vol], self.sineGenArray)
            # add in the clicks and dings. These are arbitrary, and you can
            # do without them if you want (just make a parameter that cancels
            # it out, w/e idc) or you can do just clicks, just dings,
            # you could make them dog woofs, it's all good. Just a note that
            # you *should* use mono files for the dividers, but if you have a
            # stereo file, use the template I have for the ding track.

            if c_vol % 6 == 0:
                a2 = sp.read(os.path.join('waves','ding.wav'))[1].T[0][0:8503]

            else:
                a2 = sp.read(os.path.join('waves','click.wav'))[1]
            tmp.append(np.concatenate((a2, a1)))
        return tmp

    def stereoSigGen(self):
        """
        Takes the mono signals, turns it into a stereo signal, now with HRTFs
        applied.

        Takes the mono signals, doubles each one, applies the appropriate
        left/right HRTF, then adds that to a big track that should be written as
        a .wav file.

        Return:
        ------------
        Numpy 2D Array, 2 channel, np.float32
            Stereo WAV file almost ready to write. If it doesn't work,
            add in a .T on the array to transpose it.
        """

        # This part is more to just open up the HRIR files, then convert them
        # to np.float32 arrays so that you can do compatible math with them.
        # Right now, each HRIR is written in signed int16 (-32768 -> 32767),
        # so to convert to np.float32, just map 32768 = 1 by dividing
        # everything by 32768.
        #
        # The HRTF/HRIR files I found are found at:
        # http://sound.media.mit.edu/resources/KEMAR/full.zip
        # Do note that there are more recent proprietary libraries which
        # achieve HRTFs more accurately and it sounds really clean,
        # and also possible is using the .mat files that CIPIC has here:
        # http://interface.cipic.ucdavis.edu/data/CIPIC_hrtf_database.zip
        # but you'll need to do a little bit (see: a shitload) of work to
        # figure out how to use mat files for this and whatnot.
        L_hrtf = [sp.read(os.path.join('hrtf','L0e%03da.wav' % (m % 360)))[
                      1] / 32768. for m in range(270, 540, 5)]
        R_hrtf = [sp.read(os.path.join('hrtf', 'R0e%03da.wav' % (m % 360)))[
                      1] / 32768. for m in range(270, 540, 5)]
        L_sig = np.empty((0, 0), dtype=np.float32)
        R_sig = np.empty((0, 0), dtype=np.float32)
        for wave in range(len(self.mono_sig)):
            # Convolution is how you apply the head related impulse response
            # to the mono signal. It's really tricky math in the time domain,
            # but because computers are good at doing simplified math and
            # because humans are good at simplifying math, just think of
            # convolution as a magic time domain function that ultimately
            # makes things sound like they're coming from the left or right.
            L_tf = np.convolve(self.mono_sig[wave], L_hrtf[wave], 'same')
            R_tf = np.convolve(self.mono_sig[wave], R_hrtf[wave], 'same')
            L_sig = np.append(L_sig, L_tf)
            R_sig = np.append(R_sig, R_tf)
        return np.asarray([L_sig, R_sig]).T
