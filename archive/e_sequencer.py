import glob
from scipy.io import wavfile as sp
import numpy as np

wavlist = sorted(glob.glob('stereo/*'))
wavlist[::12] = ['waves/ding.wav'] * len(wavlist[::12])
print wavlist
files = [sp.read(x)[1] for x in wavlist]

splice = np.concatenate(files, 0)
sp.write('full_stereo.wav', 44100, splice)