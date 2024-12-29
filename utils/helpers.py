import tkinter as tk
from tkinter import filedialog, END, messagebox
import glob
import numpy as np
import os
from skimage import io

def select_dir(entry):
    selected_dir = tk.filedialog.askdirectory()
    if selected_dir is not None and selected_dir != '':
        entry.delete(0, END)
        entry.insert(0, selected_dir)

def convert_csv_string_to_int_list(csv_string):
    """
    Converts a CSV string into a float list
    csv_string - a CSV string of floats
    Returns a list of floats, or None if the list cannot be converted
    """
    try:
        csv_string = ''.join(csv_string.split())
        float_list = [int(x) for x in csv_string.split(",")]
        return float_list
    except Exception:
        return None

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
    blankAcquisitions = convert_csv_string_to_int_list(blankAcquisitions)
    signalAcquisitions = convert_csv_string_to_int_list(signalAcquisitions)
    bracket = int(bracket)
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
    return None

def process_images1(dirname, blankAcquisitions, signalAcquisitions, bracket):
    if not (blankAcquisitions := convert_csv_string_to_int_list(blankAcquisitions)):
        messagebox.showerror("Error", "Blank acquisitions has to be a list of integers")
        return
    
    if not (signalAcquisitions := convert_csv_string_to_int_list(signalAcquisitions)):
        messagebox.showerror("Error", "Signal acquisitions has to be a list of integers")
        return
    
    try:
        bracket = int(bracket)
    except Exception:
        return messagebox.showerror("Error", "Number of brackets has to be a single integer number")
    
    save_dir = os.path.abspath(os.path.join(dirname,"..")) + "\\Avg_images"
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    
    for i in range(bracket):
        Blank_avg = read_and_avg_images(dirname, blankAcquisitions, i)
        fileName = 'Blank_Avg '+str(i)+'.tif'
        io.imsave(os.path.join(save_dir, fileName), Blank_avg)
    
    for i in range(bracket):
        Signal_avg = read_and_avg_images(dirname, signalAcquisitions, i)
        fileName = 'Signal_Avg '+str(i)+'.tif'
        io.imsave(os.path.join(save_dir, fileName), Signal_avg)
    return None