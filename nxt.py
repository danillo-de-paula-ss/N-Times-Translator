# N-Times Translator
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
# import translators as ts
import os
import json
from PIL import Image, ImageTk

class App(tk.Tk):
    def __init__(self, screenName = None, baseName = None, className = "Tk", useTk = True, sync = False, use = None):
        super().__init__(screenName, baseName, className, useTk, sync, use)
        # get language codes
        with open('language_codes.json', 'rt', encoding='utf-8') as file:
            language_codes: dict[str, dict[str, str]] = json.loads(file.read())
        self.source_codes, self.target_codes = language_codes.values()
        self.source_langs = {v: k for k, v in self.source_codes.items()}
        self.target_langs = {v: k for k, v in self.target_codes.items()}
        self.sl_names = list(self.source_langs.values())
        self.tl_names = list(self.target_langs.values())

        # set configs
        ttk.Style().theme_use("clam")
        ttk.Style().configure('Style1.TButton', font=('Helvetica', 20))
        ttk.Style().configure('Style2.TButton', font=('Helvetica', 22))
        ttk.Style().configure('TSpinbox', borderwidth=1, relief=FLAT, padding=(0, 6), arrowsize=14)
        ttk.Style().configure('TLabel', font=('Helvetica', 12), borderwidth=1, relief=SOLID)
        self.title('N-Times Translator')
        if os.name == 'nt':
            self.iconbitmap('nxt.ico')
        else:
            self.icon = tk.PhotoImage(file='nxt.png')
            self.iconphoto(True, self.icon)
        self.geometry('1400x800')

        # menu
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        # print(self.cget('bg'))

        # file menu
        self.file_menu = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='Open File')
        self.file_menu.add_command(label='Save')
        self.file_menu.add_command(label='Save As')
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', command=self.quit)

        # edit menu
        self.edit_menu = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label='Edit', menu=self.edit_menu)
        self.edit_menu.add_command(label='Undo')
        self.edit_menu.add_command(label='Redo')
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Cut')
        self.edit_menu.add_command(label='Copy')
        self.edit_menu.add_command(label='Paste')

        # about menu
        self.help_menu = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label='Help', menu=self.help_menu)
        self.help_menu.add_command(label='About')

        # main frame
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # source frame
        self.sl_frame = tk.Frame(self.main_frame)
        self.sl_frame.grid(row=0, column=0, sticky=EW, padx=(0, 5))
        self.sl_frame.grid_columnconfigure(0, weight=1)

        # panel frame
        self.panel_frame = tk.Frame(self.main_frame)
        self.panel_frame.grid(row=1, column=1, sticky=NS)

        # target frame
        self.tl_frame = tk.Frame(self.main_frame)
        self.tl_frame.grid(row=0, column=2, sticky=EW, padx=(5, 0))
        self.tl_frame.grid_columnconfigure(0, weight=1)
        
        # source frame config
        # source language label
        self.sl_label = tk.Label(self.sl_frame, text='Source Language', font=('Helvetica', 16, 'bold'))
        self.sl_label.grid(row=0, column=0, pady=(10, 0), sticky=EW)

        # source language combo
        self.sl_combo = ttk.Combobox(self.sl_frame, values=self.sl_names, font=('Helvetica', 12))
        self.sl_combo.set(self.sl_names[0])
        self.sl_combo.grid(row=1, column=0, pady=(0, 2), padx=(1, 0), ipady=7, sticky=EW)

        # paste text button
        self.paste_img = ImageTk.PhotoImage(Image.open('buttons/paste.png').resize((30, 30), reducing_gap=1.0))
        self.sl_paste_btn = ttk.Button(self.sl_frame, image=self.paste_img, padding=(0, 0))
        self.sl_paste_btn.grid(row=1, column=1, pady=(0, 2), padx=4)

        # open text button
        self.open_text_img = ImageTk.PhotoImage(Image.open('buttons/open-file.png').resize((30, 30), reducing_gap=1.0))
        self.sl_open_text_btn = ttk.Button(self.sl_frame, image=self.open_text_img, padding=(0, 0))
        self.sl_open_text_btn.grid(row=1, column=2, pady=(0, 2))

        # source language textbox frame
        self.sl_text_frame = tk.Frame(self.main_frame)
        self.sl_text_frame.grid(row=1, column=0, padx=(0, 5), sticky=NSEW)

        # source language textbox v scrollbar
        self.sl_text_v_scroll = tk.Scrollbar(self.sl_text_frame, orient=VERTICAL)
        self.sl_text_v_scroll.pack(side=RIGHT, fill=Y, pady=(1, 0))

        # source language textbox h scrollbar
        self.sl_text_h_scroll = tk.Scrollbar(self.sl_text_frame, orient=HORIZONTAL)
        self.sl_text_h_scroll.pack(side=BOTTOM, fill=X, padx=(1, 0))

        # source language textbox
        self.sl_text = tk.Text(self.sl_text_frame, width=50, height=20, font=('Helvetica', 12), yscrollcommand=self.sl_text_v_scroll.set, xscrollcommand=self.sl_text_h_scroll.set, wrap=NONE)
        self.sl_text.pack(fill=BOTH, expand=True)

        # config source language textbox scrollbars
        self.sl_text_v_scroll.config(command=self.sl_text.yview)
        self.sl_text_h_scroll.config(command=self.sl_text.xview)

        # panel frame config
        # switch languages button
        self.swap_img = ImageTk.PhotoImage(Image.open('buttons/switch.png').resize((80, 80), reducing_gap=1.0))
        self.swap_language_btn = ttk.Button(self.panel_frame, text='Switch Languages', image=self.swap_img, padding=(0, 0), compound=TOP, style='Style1.TButton')
        self.swap_language_btn.pack(ipadx=10, ipady=10)

        # push element
        self.push = tk.Text(self.panel_frame, font='_ 1', bd=0, padx=0, pady=0, width=0, state=DISABLED, bg='#d9d9d9')
        self.push.pack(fill=Y, expand=True)

        # translation times frame
        self.trans_times_frame = tk.Frame(self.panel_frame)
        self.trans_times_frame.pack()

        # translation times label 1
        self.trans_times_label_1 = ttk.Label(self.trans_times_frame, text='Translate', anchor=CENTER)
        self.trans_times_label_1.grid(row=0, column=0, ipadx=6, ipady=6)

        # translation times spin
        self.trans_times_spin = ttk.Spinbox(self.trans_times_frame, from_=0, to=1000, font=('Helvetica', 12), width=10)
        self.trans_times_spin.set(0)
        self.trans_times_spin.grid(row=0, column=1)

        # translation times label 2
        self.trans_times_label_2 = ttk.Label(self.trans_times_frame, text='times', anchor=CENTER)
        self.trans_times_label_2.grid(row=0, column=2, ipadx=6, ipady=6)

        # start button
        self.start_button = ttk.Button(self.panel_frame, text='Start Translation!', padding=(0, 0), style='Style2.TButton')
        self.start_button.pack(pady=(10, 0), ipadx=8, ipady=8)

        # push element
        self.push = tk.Text(self.panel_frame, font='_ 1', bd=0, padx=0, pady=0, width=0, state=DISABLED, bg='#d9d9d9')
        self.push.pack(fill=Y, expand=True)

        # target frame config
        # target language label
        self.tl_label = tk.Label(self.tl_frame, text='Target Language', font=('Helvetica', 16, 'bold'))
        self.tl_label.grid(row=0, column=0, pady=(10, 0), sticky=EW)

        # target language combo
        self.tl_combo = ttk.Combobox(self.tl_frame, values=self.tl_names, font=('Helvetica', 12))
        self.tl_combo.set(self.tl_names[58])
        self.tl_combo.grid(row=1, column=0, pady=(0, 2), padx=(1, 0), ipady=7, sticky=EW)

        # copy text button
        self.copy_img = ImageTk.PhotoImage(Image.open('buttons/copy.png').resize((30, 30), reducing_gap=1.0))
        self.tl_copy_btn = ttk.Button(self.tl_frame, image=self.copy_img, padding=(0, 0))
        self.tl_copy_btn.grid(row=1, column=1, pady=(0, 2), padx=4)

        # open text button
        self.save_text_img = ImageTk.PhotoImage(Image.open('buttons/diskette.png').resize((30, 30), reducing_gap=1.0))
        self.tl_save_text_btn = ttk.Button(self.tl_frame, image=self.save_text_img, padding=(0, 0))
        self.tl_save_text_btn.grid(row=1, column=2, pady=(0, 2))

        # target language textbox frame
        self.tl_text_frame = tk.Frame(self.main_frame)
        self.tl_text_frame.grid(row=1, column=2, padx=(5, 0), sticky=NSEW)

        # target language textbox v scrollbar
        self.tl_text_v_scroll = tk.Scrollbar(self.tl_text_frame, orient=VERTICAL)
        self.tl_text_v_scroll.pack(side=RIGHT, fill=Y, pady=(1, 0))

        # target language textbox h scrollbar
        self.tl_text_h_scroll = tk.Scrollbar(self.tl_text_frame, orient=HORIZONTAL)
        self.tl_text_h_scroll.pack(side=BOTTOM, fill=X, padx=(1, 0))

        # target language textbox
        self.tl_text = tk.Text(self.tl_text_frame, width=50, height=20, font=('Helvetica', 12), yscrollcommand=self.tl_text_v_scroll.set, xscrollcommand=self.tl_text_h_scroll.set, wrap=NONE)
        self.tl_text.pack(fill=BOTH, expand=True)

        # config target language textbox scrollbars
        self.tl_text_v_scroll.config(command=self.tl_text.yview)
        self.tl_text_h_scroll.config(command=self.tl_text.xview)

        # progress bar
        self.progress_bar = ttk.Progressbar(self)
        self.progress_bar.pack(fill=X, pady=(10, 0))

        # progress label
        self.progress_label = tk.Label(text='source: en, target: pt, times: 10, progress: 100%, status: Complete!    ', anchor=E, bd=1, relief=SUNKEN)
        self.progress_label.pack(fill=X, side=BOTTOM)

if __name__ == '__main__':
    app = App()
    app.mainloop()
