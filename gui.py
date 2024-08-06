import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from idlelib.tooltip import Hovertip

import sv_ttk

window = None
icon = None

def create_gui(func):
    global window, icon
    window = tk.Tk()
    icon = tk.PhotoImage(file=os.path.join(sys._MEIPASS, './icon.png') if getattr(sys, 'frozen', False) else './icon.png')
    window.title('Statistical App Generator')
    window.iconphoto(True, icon)

    frame = ttk.Frame(window)
    label = ttk.Label(frame, text='Generates a stats web app from a template')
    label.pack(pady=20)
    math_inp = createBrowseButton(frame, 'Math File', "Path to a .py or .r file, containing a function (named 'calc' unless otherwise specified in config), which does math given an argument object and outputs an object", title='Select a calculation file', filetypes=[('Statistics Files', '.r .py')])
    config_inp = createBrowseButton(frame, 'Configuration File', "Path to a .JSON file (format in README.md) for app configuration", title='Select a config file', filetypes=[('JSON Configuration Files', '.json')])
    outp_inp = createBrowseButton(frame, 'Output Directory', "Relative or absolute path where an 'app' directory should be generated containing the application", folder=True, title='Select a calculation file')
    
    btn_frame = ttk.Frame(frame)
    gen = ttk.Button(btn_frame, text='Generate', command=lambda: func({'math_filepath': math_inp.get(), 'config': config_inp.get(), 'out': outp_inp.get()}, True))
    gen.grid(row=0, column=0, padx=5, pady=15)
    cancel = ttk.Button(btn_frame, text='Cancel', command=lambda: sys.exit(0))
    cancel.grid(row=0, column=1, padx=5, pady=15)
    btn_frame.pack()

    frame.pack(fill='x', padx=25, pady=20)
    sv_ttk.set_theme('light')
    style = ttk.Style()
    style.configure('small.TButton', font=(None, 7))
    window.protocol('WM_DELETE_WINDOW', lambda: sys.exit(0))
    window.mainloop()

def createBrowseButton(window, argname, help, folder=False, **kwargs):
    frame = ttk.Frame(window)
    label = ttk.Label(frame, text=argname)
    label.grid(row=0, column=0, padx=5)
    help_btn = ttk.Button(frame, text='?', style="small.TButton")
    help_btn.grid(row=0, column=1, padx=5)
    Hovertip(help_btn, help)
    inp = ttk.Entry(frame)
    inp.grid(row=0, column=2, padx=5, sticky='we')
    def set_text(text):
        inp.delete(0, tk.END)
        inp.insert(0, text)
    if not folder:
        btn = ttk.Button(frame, text="Browse", command=lambda: set_text(filedialog.askopenfilename(**kwargs)))
    else:
        btn = ttk.Button(frame, text="Browse", command=lambda: set_text(filedialog.askdirectory(**kwargs)))
    btn.grid(row=0, column=3, padx=5)
    frame.columnconfigure(2, weight=1)
    frame.pack(pady=5, fill='x')
    return inp

def create_exc(exc):
    window = tk.Tk()
    window.title('Statistical App Generator')

    frame = ttk.Frame(window)
    label = ttk.Label(frame, text=f'An error occurred: {exc}')
    label.pack()
    btn = ttk.Button(frame, text='OK', command=lambda: window.destroy())
    btn.pack(pady=5)
    
    frame.pack(fill='x', padx=25, pady=20)
    window.mainloop()

def show_success_msg(path):
    window = tk.Tk()
    window.title('Statistical App Generator')

    frame = ttk.Frame(window)
    label = ttk.Label(frame, text=f'App generated at {path}')
    label.pack()
    btn = ttk.Button(frame, text='OK', command=lambda: sys.exit(0))
    btn.pack(pady=5)
    
    frame.pack(fill='x', padx=25, pady=20)
    window.protocol('WM_DELETE_WINDOW', lambda: sys.exit(0))
    window.mainloop()