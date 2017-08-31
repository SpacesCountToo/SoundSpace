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
from img_deconstruct import Image
from sound_reconstruct import SoundSpace
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt #*
import numpy as np
import Tkinter as tk            #*
import tkFileDialog as fd       #*
import os
import sys                      #*

#* things with the asterisk mean that it's kinda just extra stuff that you
# only need for the main file. Matplotlib is extra if you just want the
# sound, the Tkinter stuff is extra if you want like a file dialog thing.
# Everything that's necessary calls is not marked in asterisks.

# TO DO:
# Clean this shit up.
# [x] Image deconstruction
# [x] Data object from deconstruction
# [x] Sound reconstruction
#     To revamp:
#         Combine sound gen and sound hrtf patch to one object
# [x] Clean up main :)
# [x] Add progress text
# [ ] Add documentation to the libraries


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
axes[1].imshow(a.reduction.T, origin='lower', cmap='gist_stern')

print 'Finalizing wav writes and png writes...'

wav.write(os.path.join(dire, 'fast_%s.wav' % a.name), 44100, fast.stereo_sig)
wav.write(os.path.join(dire, 'slow_%s.wav' % a.name), 44100, slow.stereo_sig)
fig.savefig(os.path.join(dire, '%s.svg' % a.name), format='svg', dpi=1200)

print 'Done. :)'
plt.show()
