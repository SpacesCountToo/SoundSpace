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
# [ ] Clean up main :)


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

a = Image(filename)
fast = SoundSpace(a.reduction, 1.0)
slow = SoundSpace(a.reduction, 3.0)

dire = 'objects/%s' % a.name
try:
    os.makedirs(dire)
except OSError:
    if not os.path.isdir(dire):
        raise

fig, axes = plt.subplots(nrows=1, ncols=2)
axes[0].imshow(np.log10(a.data.T), origin='lower', cmap='RdBu')
axes[1].imshow(a.reduction.T, origin='lower', cmap='RdYlGn')

print 'Finalizing wav writes and png writes...'

wav.write('%s/fast_%s.wav' % (dire, a.name), 44100, fast.stereo_sig.T)
wav.write('%s/slow_%s.wav' % (dire, a.name), 44100, slow.stereo_sig.T)
fig.savefig('%s/%s.png' % (dire, a.name))

print 'Cleaning up!'

for x in glob.glob('stereo/*') + glob.glob('waves/*_*'):
    os.remove(x)

print 'Done. :)'
plt.show()
