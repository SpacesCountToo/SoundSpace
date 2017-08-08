import numpy as np
from img_deconstruct import Image
import scipy.io.wavfile as sp

class SoundSpace:

    def __init__(self, volume_list, notetime):
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
        tmp = []

        for c_vol in range(len(self.volumes)):
            a1 = np.dot(self.volumes[c_vol], self.sineGenArray)
            if c_vol % 6 == 0:
                a2 = sp.read('waves/ding.wav')[1].T[0][0:8503]

            else:
                a2 = sp.read('waves/click.wav')[1]
            tmp.append(np.concatenate((a2, a1)))
        return tmp

    def stereoSigGen(self):
        L_hrtf = [sp.read('hrtf/L0e%03da.wav' % (m % 360))[1]/32768.
                  for m in range(270, 540, 5)]
        R_hrtf = [sp.read('hrtf/R0e%03da.wav' % (m % 360))[1]/32768.
                  for m in range(270, 540, 5)]
        L_sig = np.empty((0, 0), dtype=np.float32)
        R_sig = np.empty((0, 0), dtype=np.float32)
        for wave in range(len(self.mono_sig)):
            L_tf = np.convolve(self.mono_sig[wave], L_hrtf[wave], 'same')
            R_tf = np.convolve(self.mono_sig[wave], R_hrtf[wave], 'same')
            L_sig = np.append(L_sig, L_tf)
            R_sig = np.append(R_sig, R_tf)
        return np.asarray([L_sig, R_sig])

a = Image('pix/m13_g-band_45sec_bin2_2016jun24_lindsaymberkhout_num12_seo.fits')
x = SoundSpace(a.reduction, 1.0)
sp.write('fast.wav', 44100, x.stereo_sig.T)