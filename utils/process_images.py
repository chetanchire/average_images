import numpy as np
import os

def process_images(dirname, blankAcquisitions, signalAcquisitions, bracket):
    save_dir = os.path.abspath(os.path.join(dirname,".."))+"\\Avg_images"
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    for i in range(bracket):
        Blank_avg = read_and_avg_images(dirname, blankAcquisitions, i)
        fileName = 'Blank_Avg '+str(i)+'.tif'
        io.imsave(os.path.join(save_dir,fileName), Blank_avg)
    for i in range(bracket):
        Signal_avg = read_and_avg_images(dirname, signalAcquisitions, i)
        fileName = 'Signal_Avg '+str(i)+'.tif'
        io.imsave(os.path.join(save_dir,fileName), Signal_avg)