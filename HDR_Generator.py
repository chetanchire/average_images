import numpy as np
import glob
import os
import imageio
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, END, W
from datetime import datetime

def select_dir(entry):
    """
    Prompts the user to select a directory, then writes that path to the input tk.Entry
    If the prompt is closed without selection, don't write the blank path
    entry - the tk.Entry to write the selected directory path into
    """
    selected_dir = filedialog.askdirectory()
    if selected_dir is not None and selected_dir != '':
        entry.delete(0, END)
        entry.insert(0, selected_dir)

def convert_csv_string_to_float_list(csv_string):
    """
    Converts a CSV string into a float list
    csv_string - a CSV string of floats
    Returns a list of floats, or None if the list cannot be converted
    """
    try:
        csv_string = ''.join(csv_string.split())
        float_list = [float(x) for x in csv_string.split(",")]
        return float_list
    except Exception:
        return None

def generate_hdr_image(image_bracket_paths, T_exp, I_led, output_file_path):
    """
    Generate an HDR image from a bracket of raw images
    image_bracket_paths - an ordered list of images to generate the HDR from
    T_exp - a list of the exposure lengths used in the bracket
    I_led - a list of the LED intensities used in the bracket
    output_file_path - save location for the output HDR image
    """
    N_sat = int(2**16 * .5)
    N_exp = len(image_bracket_paths)
    signal_images = [np.asarray(Image.open(x), dtype=np.float32) for x in image_bracket_paths]

    # Start with the brightest image, and iteratively replace any pixels that are still saturated 
    # with the next dimmest image's pixels
    Sacc = signal_images[0] / (T_exp[0] * I_led[0] * 10**-6)

    for i in range(1, N_exp):
        Snew = signal_images[i] / (T_exp[i] * I_led[i] * 10**-6)
        Sacc[signal_images[i-1] > N_sat] = Snew[signal_images[i-1] > N_sat]

    # Scale back down to 16-bit
    Sacc = Sacc / 256

    # Set any negative pixel values to zero
    Sacc[Sacc < 0] = 0

    # Round to nearest integer pixel value and formally cast to 16-bit
    Sacc = Sacc.round().astype(np.uint16)

    # Save the HDR images
    hdr_image = Image.fromarray(Sacc)
    hdr_image.save(output_file_path)

def generate_autofocus_hdr_images(raw_image_folder, output_folder):
    """
    Generates the HDR images used for autofocus
    raw_image_folder- the folder containing the images taken to autofocus on
    output_folder - the folder to write the HDR images to
    Dev note - currently hard-coding exposure lengths + LED intensities
    TODO - have the Korvis App pass back the brackets it actually used instead of hard-coding
    """
    T_exp = [7272, 3636, 1818, 909, 455, 228]
    I_led = [12.4, 12.4, 12.4, 12.4, 12.4, 12.4]
    image_paths = glob.glob(raw_image_folder + "/*.tif")
    image_paths.sort(key=os.path.getmtime)

    for i in range(0, len(image_paths), 6):
        output_file_path = output_folder + "/Autofocus HDR " + str(i//6) + ".tif"
        generate_hdr_image(image_paths[i:i+6], T_exp, I_led, output_file_path)

def generate_hdr_images(image_dir, T_exp, I_led, signal_folder, blank_folder, signal_file_name, blank_file_name, skip_test_images=False, bit_depth=16):
    """
    Generates HDR images for the blank images and the signal images in the selected folder.
    image_dir - a path to the directory containing the images
    T_exp - a list of the exposure lengths used in the run
    I_led - a list of the LED intensities used in the run
    signal_folder - folder to save the signal HDR file to
    blank_folder - folder to save the blank HDR file to
    signal_file_name - file name for the signal HDR image (without extension)
    blank_file_name - file name for the blank HDR image (without extension)
    skip_test_images - True if there are no test images in the folder (so the blanks are the first bracket instead of the second)
    bit_depth - the bit depth of the images. Defaults to 16 because we work with TIFs

    Returns None if successful, or an error string if something went wrong

    Notes - This method assumes that the blank image bracket is the second bracket taken
    (or the first if skip_test_images is True), and that the signal image bracket is
    the final bracket taken.
    """
    N_sat = int(2**bit_depth * .5)

    # Validate image_dir file path
    if not os.path.exists(image_dir):
        return "The selected image folder path could not be found. Please check the selected path."

    N_exp = len(T_exp)

    if N_exp != len(I_led):
        return "The length of Exposure Lengths (ms) does not match the length of LED Intensities (mA)."

    # Gather + sort images from selected image folder
    tif_paths = glob.glob(image_dir + "/*.tif")
    tif_paths.sort(key=os.path.getmtime)

    # Show an error if there are not enough images in the selected folder to generate the HDR images.
    # Only two brackets are necessary for processing (blanks + signal), but currently in real runs we
    # include a test image bracket that isn't processed, so we treat the minimum as three in that case
    MIN_NUM_BRACKETS = 2 if skip_test_images else 3
    if len(tif_paths) < MIN_NUM_BRACKETS * N_exp:
        return "There are not enough images in the selected image folder to generate HDR images. Please confirm that you have selected the correct folder."

    # Load blank and signal images into ndarrays
    # The blanks are the second image bracket in the folder if test images were not skipped,
    # else they are the first. The signal images are always the final bracket.
    blank_image_paths = tif_paths[0 : N_exp] if skip_test_images else tif_paths[N_exp : 2*N_exp]
    signal_image_paths = tif_paths[len(tif_paths) - N_exp : len(tif_paths)]

    blank_images = [np.asarray(Image.open(x), dtype=np.float32) for x in blank_image_paths]
    signal_images = [np.asarray(Image.open(x), dtype=np.float32) for x in signal_image_paths]

    # Start with the brightest image, and iteratively replace any pixels that are saturated 
    # with the next dimmest image's pixels
    Sacc = signal_images[0] / (T_exp[0] * I_led[0] * 10**-6)
    Bacc = blank_images[0] / (T_exp[0] * I_led[0] * 10**-6)

    for i in range(1, N_exp):
        Snew = signal_images[i] / (T_exp[i] * I_led[i] * 10**-6)
        Bnew = blank_images[i] / (T_exp[i] * I_led[i] * 10**-6)

        Sacc[signal_images[i-1] > N_sat] = Snew[signal_images[i-1] > N_sat]
        Bacc[blank_images[i-1] > N_sat] = Bnew[blank_images[i-1] > N_sat]

    # Blank subtract from signal
    Sacc = Sacc - Bacc

    # Scale back down to 16-bit
    Sacc = Sacc / 256
    Bacc = Bacc / 256

    # Set any negative pixel values to zero
    Sacc[Sacc < 0] = 0
    Bacc[Bacc < 0] = 0

    # Round to nearest integer pixel value and formally cast to 16-bit
    Sacc = Sacc.round().astype(np.uint16)
    Bacc = Bacc.round().astype(np.uint16)

    # Save the HDR images
    blank_hdr_image = Image.fromarray(Bacc)
    signal_hdr_image = Image.fromarray(Sacc)
    blank_hdr_image.save(blank_folder + "/" + blank_file_name + ".tif")
    signal_hdr_image.save(signal_folder + "/" + signal_file_name + ".tif")

    # Return None to indicate successful image generation
    return None

def generate_hdr_images_standalone(image_dir, T_exp, I_led, skip_test_images, is_reprocess, bit_depth=16):
    """
    Wrapper function for the applet version so that it can display messageboxes
    """
    # Convert + validate Exposure Lengths + LED Intensities
    if not (T_exp := convert_csv_string_to_float_list(T_exp)):
        messagebox.showerror("Error", "Exposure Lengths (ms) is invalid. It must be a comma-separated list of numbers.")
        return

    if not (I_led := convert_csv_string_to_float_list(I_led)):
        messagebox.showerror("Error", "LED Intensities (mA) is invalid. It must be a comma-separated list of numbers.")
        return

    if not is_reprocess:
        res = generate_hdr_images(image_dir, T_exp, I_led, image_dir, image_dir, "HDR Signal", "HDR Blank", skip_test_images, bit_depth)
    else:
        res = reprocess_run_folder(image_dir, T_exp, I_led)

    if res:
        messagebox.showerror("Error", res)

def reprocess_run_folder(run_folder, T_exp, I_led):
    """
    Regenerates the HDRs for an entire run, backing up the existing improc folder so that the old images can
    be compared against

    run_folder - the run folder to regenerate the HDRs for
    T_exp - the exposure bracket used for the run
    I_led - the LED intensity bracket used for the run
    """
    os.rename(run_folder + "/improc", run_folder + "/improc backup - " + datetime.now().strftime("%Y-%m-%d %H%M%S"))
    os.mkdir(run_folder + "/improc")

    blank_folder = run_folder + "/improc/blank"
    signal_folder = run_folder + "/improc/signal"
    os.mkdir(blank_folder)
    os.mkdir(signal_folder)

    cycle_folders = glob.glob(run_folder + "/[0-9][0-9][0-9] - *")
    for cycle_folder in cycle_folders:
        cycle_name = os.path.basename(os.path.normpath(cycle_folder))
        generate_hdr_images(cycle_folder + "/Images", T_exp, I_led, signal_folder, blank_folder, cycle_name + " Signal", cycle_name + " Blank", skip_test_images=False, bit_depth=16)

    # Return None if completed successfully
    return None 

if __name__ == "__main__":
    # Create the main window
    main_window = tk.Tk()
    main_window.title("HDR Generator")
    
    # Image directory selection controls
    tk.Label(text="Image folder (Run Folder if reprocessing): ").grid(row=0, column=0)
    image_dir = tk.Entry(width=100)
    image_dir.grid(row=0, column=1, padx=2, pady=2)
    image_dir_btn = tk.Button(text="...", command=lambda:select_dir(image_dir))
    image_dir_btn.grid(row=0, column=2, padx=3)
    
    # T_exp entry controls
    tk.Label(text="Exposure Lengths (ms): ").grid(row=1, column=0)
    T_exp_entry = tk.Entry(width=100)
    T_exp_entry.grid(row=1, column=1)
    T_exp_entry.insert(0, "7272, 3636, 1818, 909, 455, 228")
    
    # LED Intensity controls
    tk.Label(text="LED Intensities (mA): ").grid(row=2, column=0)
    led_intensity_entry = tk.Entry(width=100)
    led_intensity_entry.grid(row=2, column=1)
    led_intensity_entry.insert(0, "12.4, 12.4, 12.4, 12.4, 12.4, 12.4")
    
    # No test images checkbutton
    tk.Label(text="Skipped Test Images").grid(row=3, column=0)
    is_skip_checked = tk.IntVar()
    skip_checkbutton = tk.Checkbutton(variable=is_skip_checked)
    skip_checkbutton.grid(row=3, column=1, sticky=W)

    # Reprocess existing run checkbutton
    tk.Label(text="Reprocess Existing Run").grid(row=4, column=0)
    is_reprocess_checked = tk.IntVar()
    reprocess_checkbutton = tk.Checkbutton(variable=is_reprocess_checked)
    reprocess_checkbutton.grid(row=4, column=1, sticky=W)
    
    # Button
    tk.Button(text="Generate HDR Images", command=lambda:generate_hdr_images_standalone(image_dir.get(), T_exp_entry.get(), led_intensity_entry.get(), is_skip_checked.get(), is_reprocess_checked.get())).grid(row=5, column=0, columnspan=2, pady=5)
    
    main_window.eval('tk::PlaceWindow . center')
    main_window.mainloop()