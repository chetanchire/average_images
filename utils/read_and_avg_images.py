import numpy as np
from skimage import io
import glob
import os

def read_and_avg_images(dirname, acquisitions, bracket_no):
    images = []
    for i in range(len(acquisitions)):
        file = '* ' + str(acquisitions[i] + bracket_no) + '.tif'
        images.append(io.imread(glob.glob(os.path.join(dirname, file))[0], plugin = 'pil'))
    sum_Images = np.empty_like(images[0])
    for i in range(len(images)):
        sum_Images = sum_Images + images[i].astype(np.float32) if sum_Images.size != 0 else images[i]
    Average_Image = sum_Images / len(images)
    return Average_Image.astype(np.uint16)