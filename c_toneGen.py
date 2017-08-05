import scipy.io.wavfile as sp
import numpy as np
import matplotlib.pyplot as plt

class SineGen:

    def __init__(self, volume_list, column_no, notetime):
        self.notes = [110., 116.54, 123.47, 130.81, 138.59, 146.83,
                      155.56, 164.81, 174.61, 185., 196., 207.65,
                      220., 233.08, 246.94, 261.63, 277.18, 293.66,
                      311.13, 329.63, 349.23, 369.99, 392., 415.30,
                      440., 466.16, 493.88, 523.25, 554.37, 587.33,
                      622.25, 659.25, 698.46, 739.99, 783.99, 830.61]

        self.framerate = 44100
        self.notetime = notetime
        self.framect = self.framerate*self.notetime
        self.volumes = volume_list
        self.tsunami = np.zeros(int(self.framect), np.float32)
        self.filename = 'mono_%d.wav' % column_no
        self.click = sp.read('waves/click.wav')
        self.click = self.click[1]
        self.splash()
        # if np.abs(self.tsunami).max() == 0:
        #     print self.tsunami
        # else:
        #     print self.tsunami/np.abs(self.tsunami).max()

    def splash(self):
        # get it? splash = make waves? HEHEHEHEHE
        # nothing happened...
        for index in range(len(self.volumes)):
            frequency = self.notes[index]
            volume = self.volumes[index]
            x = np.linspace(0, 2*np.pi*self.notetime, self.framect)
            y = volume * np.sin(frequency * x)
            self.tsunami = np.add(self.tsunami, y)
