import scipy.io.wavfile as wave
import scipy.signal as sp
import numpy as np
import glob


class Transform:
    def __init__(self, mono_file, speed):
        self.speed = speed
        L_hrtf           = ['hrtf/L0e%03da.wav' % (x % 360)
                            for x in range(270, 540, 5)]
        R_hrtf           = ['hrtf/R0e%03da.wav' % (x % 360)
                            for x in range(270, 540, 5)]
        index_list       = ['%02d' % x for x in range(36)]
        self.tftable     = dict(zip(index_list, zip(L_hrtf, R_hrtf)))
        self.index       = mono_file[11:13]
        self.hrtf_select = self.tftable[self.index]
        self.insound     = wave.read(mono_file)
        self.insound     = self.insound[1]
        self.outsound    = 0
        self.outclick    = 0
        self.transform_sound()
        wave.write('stereo/%s_%s_stereo.wav' % (self.speed, self.index), 44100,
                   self.outsound.T)
        wave.write('stereo/%s_%s_click.wav'  % (self.speed, self.index), 44100,
                   self.outclick.T)

    def transform_sound(self):
        stereo_prime = []
        stereo_click = []
        for ear in range(2):
            hrir = wave.read(self.hrtf_select[ear])
            hrir = hrir[1]/32768.
            stereo_prime.append(np.convolve(self.insound, hrir, 'same'))
            stereo_click.append(np.convolve(hrir, hrir, 'same'))
        self.outsound = np.asarray(stereo_prime, dtype=np.float32)
        self.outclick = np.asarray(stereo_click, dtype=np.float32)
