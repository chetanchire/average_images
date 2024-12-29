import tkinter as tk
from tkinter import filedialog, END

def select_dir(entry):
    selected_dir = tk.filedialog.askdirectory()
    if selected_dir is not None and selected_dir != '':
        entry.delete(0, END)
        entry.insert(0, selected_dir)