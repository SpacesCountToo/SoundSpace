from img_deconstruct import Image
from sound_reconstruct import SoundSpace
import scipy.io.wavfile as wav
import glob
import matplotlib.pyplot as plt
import numpy as np
import Tkinter as tk
import tkFileDialog as fd
import os
import sys

# TO DO:
# Clean this shit up.
# [x] Image deconstruction
# [x] Data object from deconstruction
# [x] Sound reconstruction
#     To revamp:
#         Combine sound gen and sound hrtf patch to one object
# [x] Clean up main :)
# [ ] Add progress text


# Image Select

root = tk.Tk()
root.withdraw()
FILEOPENOPTIONS = dict(defaultextension='.fits',
                       filetypes=[('FITS file','*.fits')])
print 'Selecting images...'
filename = fd.askopenfilename(**FILEOPENOPTIONS)
try:
    print 'Done. Opening %s' % filename
except TypeError:
    sys.exit('No file found, quitting...')

print "Deconstructing Image..."
a = Image(filename)
print "Done."
print "Creating fast map..."
fast = SoundSpace(a.reduction, 1.0)
print "Creating slow map..."
slow = SoundSpace(a.reduction, 3.0)
print "Done."
dire = 'objects/%s' % a.name
try:
    os.makedirs(dire)
except OSError:
    if not os.path.isdir(dire):
        raise

print "Plotting your demis- I mean, downf- I mean, images :)"
fig, axes = plt.subplots(nrows=1, ncols=2)
axes[0].imshow(np.log10(a.data.T), origin='lower', cmap='gist_stern')
axes[1].imshow(a.reduction.T, origin='lower', cmap='gist_earth')

print 'Finalizing wav writes and png writes...'

wav.write('%s/fast_%s.wav' % (dire, a.name), 44100, fast.stereo_sig.T)
wav.write('%s/slow_%s.wav' % (dire, a.name), 44100, slow.stereo_sig.T)
fig.savefig('%s/%s.png' % (dire, a.name))

print 'Done. :)'
plt.show()
