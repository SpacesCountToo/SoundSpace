import numpy as np
from img_deconstruct import Image
import scipy.io.wavfile as sp

class SoundSpace:

    def __init__(self, volume_list, notetime):
        """
        Initializes the SoundSpace object.

        Starts an object that converts all the sounds

        Parameters:
        ------------
        volume_list : Numpy 2d array in np.float32
            Contains a matrix of data relating to pixel intensity
        notetime : float
            Basically the duration of the chord you want played (in seconds)

        (important) Properties:
        ------------
        .notes : list, int
            list of frequencies. You can change this to whatever values you
            want, I have it set to half step intervals from A2 to almost A5 I
            think
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

        self.notes = [110., 116.54, 123.47, 130.81, 138.59, 146.83,
                      155.56, 164.81, 174.61, 185., 196., 207.65,
                      220., 233.08, 246.94, 261.63, 277.18, 293.66,
                      311.13, 329.63, 349.23, 369.99, 392., 415.30,
                      440., 466.16, 493.88, 523.25, 554.37, 587.33,
                      622.25, 659.25, 698.46, 739.99, 783.99, 830.61]

        self.framerate = 44100
        self.notetime = notetime
        self.framect = int(self.framerate*self.notetime)
        self.volumes = volume_list
        self.x_spc = np.linspace(0, 2*np.pi*self.notetime, self.framect)
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

        # idk, this is just doing element by element multiplication in array.
        # They call it dot multiplication in NumPy.
        for c_vol in range(len(self.volumes)):
            a1 = np.dot(self.volumes[c_vol], self.sineGenArray)
            # add in the clicks and dings. These are arbitrary, and you can
            # do without them if you want (just make a parameter that cancels
            # it out, w/e idc) or you can do just clicks, just dings,
            # you could make them dog woofs, it's all good. Just a note that
            # you *should* use mono files for the dividers, but if you have a
            # stereo file, use the template I have for the ding track.

            if c_vol % 6 == 0:
                a2 = sp.read('waves/ding.wav')[1].T[0][0:8503]

            else:
                a2 = sp.read('waves/click.wav')[1]
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
        L_hrtf = [sp.read('hrtf/L0e%03da.wav' % (m % 360))[1]/32768.
                  for m in range(270, 540, 5)]
        R_hrtf = [sp.read('hrtf/R0e%03da.wav' % (m % 360))[1]/32768.
                  for m in range(270, 540, 5)]
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
