from a_imgSplitter import Column
from b_colSplitter import Pixel
from c_toneGen import SineGen
from d_hrtfGen import Transform
from astropy.io import fits
import scipy.io.wavfile as wav
import glob
import matplotlib.pyplot as plt
import numpy as np
import Tkinter as tk
import tkFileDialog as fd
import os
import sys
# Image Select

root = tk.Tk()
root.withdraw()
FILEOPENOPTIONS = dict(defaultextension='.fits',
                       filetypes=[('All files','*.*'), ('FITS file','*.fits')])
print 'Selecting images...'
filename = fd.askopenfilename(**FILEOPENOPTIONS)
try:
    print 'Done. Opening %s' % filename
except TypeError:
    sys.exit('No file found, quitting...')
# Image -> Columns
print 'Converting images into columns...'
a = Column(filename)
full = np.zeros((36, 36), np.float64)
print 'file dimensions: %d x %d' % (len(a.data), len(a.data[0]))
print 'new file dimensions: 36 x 36' # that's the joke

# Columns -> Pixels
print 'Extracting pixel data...'
for columns in range(0, a.size - a.resolution, a.resolution):
    a.columnSelect(columns)
    b = Pixel(a.col_data, black=a.black)
    b.resShift()

    full[columns / a.resolution] = b.adjust

ma = np.ma.masked_equal(full, 0.0, copy=False)
print 'Normalizing data...'
trim_img = full / ma.max()

# Here comes the doubles. it'd be nice to change this into a function to cut
# down on half the lines, but here we are with a quick hack :/

# Pixels -> Individual Column Sounds

print 'Generating sine tones...'
fast_array = []
slow_array = []
for index in range(len(trim_img)):
    if index % 9 == 0:
        print '%0.0f%% complete' % ((index/36.)*100)
    x = SineGen(trim_img[index], index, 1.0)
    y = SineGen(trim_img[index], index, 3.0)
    fast_array.append(x.tsunami)
    slow_array.append(y.tsunami)
print '100% complete'
fast_array = np.asarray(fast_array)
slow_array = np.asarray(slow_array)
vol_cap = np.amax(np.abs(fast_array))
print 'Normalizing summed sines...'
fast_array /= vol_cap
slow_array /= vol_cap

print 'Writing individual column wav files...'
for wave in range(len(fast_array)):
    wav.write('waves/fast_%02d.wav' % wave, x.framerate, fast_array[wave])
    wav.write('waves/slow_%02d.wav' % wave, y.framerate, slow_array[wave])

print 'Applying HRTFs...'
for wave in glob.glob('waves/fast_*'):
    Transform(wave, 'fast')
for wave in glob.glob('waves/slow_*'):
    Transform(wave, 'slow')

print 'Sequencing wav files...'
fastlist = sorted(glob.glob('stereo/fast_*'))
fastlist[::12] = ['waves/ding.wav'] * len(fastlist[::12])
ffile = [wav.read(x)[1] for x in fastlist]
fsplice = np.concatenate(ffile, 0)

slowlist = sorted(glob.glob('stereo/slow_*'))
slowlist[::12] = ['waves/ding.wav'] * len(slowlist[::12])
sfile = [wav.read(x)[1] for x in slowlist]
ssplice = np.concatenate(sfile, 0)


with fits.open(filename) as raw_file:
    raw_data = raw_file[0].data

name = filename.split('/')[-1].split('.')[0]
dire = 'objects/%s' % name
try:
    os.makedirs(dire)
except OSError:
    if not os.path.isdir(dire):
        raise

fig, axes = plt.subplots(nrows=1, ncols=2)
axes[0].imshow(np.log10(raw_data), origin='lower')
axes[1].imshow(trim_img.T, origin='lower')

print 'Finalizing wav writes and png writes...'

wav.write('%s/fast_%s.wav' % (dire, name), 44100, fsplice)
wav.write('%s/slow_%s.wav' % (dire, name), 44100, ssplice)
fig.savefig('%s/%s.png' % (dire, name))

print 'Cleaning up!'

for x in glob.glob('stereo/*') + glob.glob('waves/*_*'):
    os.remove(x)

print 'Done. :)'
plt.show()
# print vol_cap
# print sinearray
# print len(sinearray)
# plt.plot(sinearray.T)
# plt.show()
