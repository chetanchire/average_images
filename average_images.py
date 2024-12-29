import tkinter as tk
"""
from tkinter import filedialog, END
import glob
import numpy as np
import os
from skimage import io
"""
from utils import helpers

blankAcquisitions = [6, 12, 18, 24]
signalAcquisitions = [30, 36, 42, 48]
brackets = 6

"""
def select_dir(entry):
    selected_dir = tk.filedialog.askdirectory()
    if selected_dir is not None and selected_dir != '':
        entry.delete(0, END)
        entry.insert(0, selected_dir)

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
"""
window = tk.Tk()
window.title("First Applet")

label = tk.Label(window, text = "Selected folder: ").grid(row=0, column=0)
Img_dir = tk.Entry(width = 100)
Img_dir.grid(row=0, column=1, padx=5, pady=5)
Img_dir_btn = tk.Button(text="Select images folder", command = lambda:helpers.select_dir(Img_dir))
Img_dir_btn.grid(row=0, column=2, padx=2, pady=2)

tk.Label(text = "Blank exposure suffixes: ").grid(row=1, column = 0)
blank_suff = tk.Entry(width=100)
blank_suff.grid(row=1, column=1, padx=5, pady=5)
blank_suff.insert(0, "6, 12, 18, 24")

tk.Label(text = "Signal exposure suffixes: ").grid(row=2, column = 0)
signal_suff = tk.Entry(width=100)
signal_suff.grid(row=2, column=1, padx=5, pady=5)
signal_suff.insert(0, "30, 36, 42, 48")

tk.Label(text = "Number of brackets in each Acquisition: ").grid(row=3, column = 0)
Brckts = tk.Entry(width=100)
Brckts.grid(row=3, column=1, padx=5, pady=5)
Brckts.insert(0, "6")

# tk.Button(text="Generate Average Images", command = lambda: helpers.process_images(Img_dir.get(), blankAcquisitions, signalAcquisitions, brackets)).grid(row=2, column=0, columnspan=2, pady = 10)
tk.Button(text="Generate Average Images", command = lambda: helpers.process_images1(Img_dir.get(), blank_suff.get(), signal_suff.get(), Brckts.get())).grid(row=4, column=0, columnspan=2, pady = 10)

window.mainloop()