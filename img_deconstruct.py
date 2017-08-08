from astropy.io import fits
import numpy as np
import itertools as it

class Image:
    def __init__(self, image):
        self.filename = image
        self.name = image.split('/')[-1].split('.')[0]
        self.chunk_size = 36
        with fits.open(image) as img:
            self.data = img[0].data.T
        self.log_data = np.log10(self.data)
        self.x_scale = (len(self.data)) / self.chunk_size
        self.y_scale = len(self.data[0]) / self.chunk_size
        self.reduction = np.zeros((36,
                                   36))
        self.black = np.percentile(self.data, 90)
        self.lower_res()
        self.normalize()

    def lower_res(self):
        for x, y in it.product(range(self.chunk_size),
                               range(self.chunk_size)
                               ):
            self.reduction[x, y] = np.percentile(
                self.data[x * self.x_scale : (x + 1) * self.x_scale,
                          y * self.y_scale: (y + 1) * self.y_scale],
                90
            )
            if self.reduction[x, y] < self.black:
                self.reduction[x, y] = 0

    def normalize(self):
        self.reduction /= np.max([np.sum(x) for x in self.reduction])
