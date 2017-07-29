from a_imgSplitter import Column
from b_colSplitter import Pixel
import matplotlib.pyplot as plt
import numpy as np

a = Column('testfile.fits')
print a.resolution
full = np.zeros((36, 36), np.float64)
print 'file dimensions: %d x %d' % (len(a.data), len(a.data[0]))

for columns in range(0, a.size-a.resolution, a.resolution):
    a.columnSelect(columns)
    b = Pixel(a.col_data, black=a.black)
    b.resShift()

    print columns/a.resolution
    print len(b.adjust)
    print b.adjust

    full[columns/a.resolution] = b.adjust

ma = np.ma.masked_equal(full, 0.0, copy=False)
trim_img = full/ma.max()
plt.imshow(trim_img.T)
plt.show()
