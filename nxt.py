# N-Times Translator
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.constants import *
from tktooltip import ToolTip
import os
import json
from PIL import Image, ImageTk
from utilities import nxt, check_internet_connection, function_async
from itertools import cycle
import pyperclip
from multiprocessing import Process, Queue, freeze_support
from multiprocessing.connection import Connection
from queue import Empty
import logging
from typing import Callable
import getpass
from contextlib import suppress
import sys
from datetime import datetime
import webbrowser

def setup_text_widget(text_widget: tk.Text):
    def redo(event: tk.Event):
        text_widget.event_generate("<<Redo>>")
        return "break"

    text_widget.bind("<Control-y>", redo)

def find_data_paths(*pathnames: str) -> str:
    if getattr(sys, "frozen", False):
        # the application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # the application is not frozen
        # change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir, *pathnames)

class CTextbox:
    def __init__(self):
        self.textbox: tk.Text | None = None
    
    def edit_undo(self):
        if self.textbox is not None:
            with suppress(tk.TclError):
                self.textbox.edit_undo()
    
    def edit_redo(self):
        if self.textbox is not None:
            with suppress(tk.TclError):
                self.textbox.edit_redo()
    
    def cut(self):
        if self.textbox is not None:
            self.copy()
            with suppress(tk.TclError):
                self.textbox.delete("sel.first", "sel.last")

    def copy(self):
        if self.textbox is not None:
            with suppress(tk.TclError):
                text = self.textbox.get("sel.first", "sel.last")
                pyperclip.copy(text)
    
    def paste(self):
        if self.textbox is not None:
            text = pyperclip.paste()
            self.textbox.insert(END, text)

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

        # create logger
        self.logger = logging.getLogger('main')
        self.logger.setLevel(logging.DEBUG)
        # create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        # set formatter
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s', '%H:%M:%S')
        console_handler.setFormatter(console_formatter)
        # add the handler to logger
        self.logger.addHandler(console_handler)

        # config style
        s = ttk.Style()
        s.theme_use("clam")
        s.configure('Style1.TButton', font=('Helvetica', 14))
        s.configure('Style2.TButton', font=('Helvetica', 22))
        s.configure('TSpinbox', borderwidth=1, relief=FLAT, padding=(0, 6), arrowsize=14)
        s.configure('TLabel', font=('Helvetica', 12), borderwidth=1, relief=SOLID)
        s.configure('TProgressbar', foreground='green', background='green')
        s.map('TCombobox', fieldbackground=[('readonly','white')])

        # set configs
        self.title('N-Times Translator')
        if os.name == 'nt':
            self.iconbitmap('nxt.ico')
        else:
            self.icon = tk.PhotoImage(file='nxt.png')
            self.iconphoto(True, self.icon)
        self.geometry('1400x800')
        bg_color = self.cget('bg')
        self.filename = ""
        self.current_textbox = CTextbox()
        self.process = None
        self.bucket = Queue()
        self.data = {}
        self.progress_text = 'source: {source}, target: {target}, times: {times}, progress: {progress}, status: {status}' + ' ' * 4

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
        self.sl_label.grid(row=0, column=0, pady=10, sticky=EW)

        # source language combo
        self.sl_combo = ttk.Combobox(self.sl_frame, values=self.sl_names, font=('Helvetica', 12), state='readonly')
        self.sl_combo.set(self.sl_names[0])
        self.sl_combo.grid(row=1, column=0, pady=(0, 2), padx=(1, 0), ipady=7, sticky=EW)

        # paste text button
        self.paste_img = ImageTk.PhotoImage(Image.open('buttons/paste.png').resize((30, 30), reducing_gap=1.0))
        self.sl_paste_btn = ttk.Button(self.sl_frame, image=self.paste_img, padding=(0, 0), command=self.paste_text)
        self.sl_paste_btn.grid(row=1, column=1, pady=(0, 2), padx=4)
        ToolTip(self.sl_paste_btn, msg='Paste text', delay=1)

        # open file button
        self.open_file_img = ImageTk.PhotoImage(Image.open('buttons/open-file.png').resize((30, 30), reducing_gap=1.0))
        self.sl_open_file_btn = ttk.Button(self.sl_frame, image=self.open_file_img, padding=(0, 0), command=self.open_text_file)
        self.sl_open_file_btn.grid(row=1, column=2, pady=(0, 2))
        ToolTip(self.sl_open_file_btn, msg='Open file', delay=1)

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
        self.sl_text = tk.Text(self.sl_text_frame, width=50, height=20, font=('Helvetica', 12), yscrollcommand=self.sl_text_v_scroll.set, xscrollcommand=self.sl_text_h_scroll.set, wrap=NONE, undo=True)
        self.sl_text.pack(fill=BOTH, expand=True)
        setup_text_widget(self.sl_text)
        self.sl_text.bind('<Key>', self._on_key)
        self.sl_text.bind('<Button-1>', self._on_key)

        # config source language textbox scrollbars
        self.sl_text_v_scroll.config(command=self.sl_text.yview)
        self.sl_text_h_scroll.config(command=self.sl_text.xview)
        
        # switch languages config
        # switch languages button
        self.swap_img = ImageTk.PhotoImage(Image.open('buttons/switch.png').resize((40, 40), reducing_gap=1.0))
        self.swap_languages_btn = ttk.Button(self.main_frame, text='Swap Languages', image=self.swap_img, padding=(0, 0), compound=TOP, style='Style1.TButton', command=self.swap_langs)
        self.swap_languages_btn.grid(row=0, column=1, pady=(6, 0), ipadx=10, sticky=NS)

        # panel frame config
        # push element
        self.vpush1 = tk.Text(self.panel_frame, font='_ 1', cursor='', bd=0, padx=0, pady=0, width=0, state=DISABLED, bg=bg_color, highlightthickness=0)
        self.vpush1.pack(fill=Y, expand=True)

        # translation times frame
        self.ts_times_frame = tk.Frame(self.panel_frame)
        self.ts_times_frame.pack()

        # translation times label 1
        self.ts_times_label_1 = ttk.Label(self.ts_times_frame, text='Translate', anchor=CENTER)
        self.ts_times_label_1.grid(row=0, column=0, ipadx=6, ipady=6)

        # translation times spin
        self.ts_times_spin = ttk.Spinbox(self.ts_times_frame, from_=1, to=1000, font=('Helvetica', 12), width=10, validate="key", validatecommand=(self.register(self._validate), "%P"))
        self.ts_times_spin.set(4)
        self.ts_times_spin.grid(row=0, column=1)

        # translation times label 2
        self.ts_times_label_2 = ttk.Label(self.ts_times_frame, text='times', anchor=CENTER)
        self.ts_times_label_2.grid(row=0, column=2, ipadx=6, ipady=6)

        # start button
        self.start_button = ttk.Button(self.panel_frame, text='Translate!', padding=(0, 0), width=14, style='Style2.TButton', command=self.start)
        self.start_button.pack(pady=(10, 0), ipadx=8, ipady=8)

        # push element
        self.vpush2 = tk.Text(self.panel_frame, font='_ 1', cursor='', bd=0, padx=0, pady=0, width=0, state=DISABLED, bg=bg_color, highlightthickness=0)
        self.vpush2.pack(fill=Y, expand=True)

        # target frame config
        # target language label
        self.tl_label = tk.Label(self.tl_frame, text='Target Language', font=('Helvetica', 16, 'bold'))
        self.tl_label.grid(row=0, column=0, pady=10, sticky=EW)

        # target language combo
        self.tl_combo = ttk.Combobox(self.tl_frame, values=self.tl_names, font=('Helvetica', 12), state='readonly')
        self.tl_combo.set(self.tl_names[58])
        self.tl_combo.grid(row=1, column=0, pady=(0, 2), padx=(1, 0), ipady=7, sticky=EW)

        # copy text button
        self.copy_img = ImageTk.PhotoImage(Image.open('buttons/copy.png').resize((30, 30), reducing_gap=1.0))
        self.tl_copy_btn = ttk.Button(self.tl_frame, image=self.copy_img, padding=(0, 0), command=self.copy_text)
        self.tl_copy_btn.grid(row=1, column=1, pady=(0, 2), padx=4)
        ToolTip(self.tl_copy_btn, msg='Copy text', delay=1)

        # save text button
        self.save_text_img = ImageTk.PhotoImage(Image.open('buttons/diskette.png').resize((30, 30), reducing_gap=1.0))
        self.tl_save_text_btn = ttk.Button(self.tl_frame, image=self.save_text_img, padding=(0, 0), command=self.save_text)
        self.tl_save_text_btn.grid(row=1, column=2, pady=(0, 2))
        ToolTip(self.tl_save_text_btn, msg='Save text to a file', delay=1)

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
        self.tl_text = tk.Text(self.tl_text_frame, width=50, height=20, font=('Helvetica', 12), yscrollcommand=self.tl_text_v_scroll.set, xscrollcommand=self.tl_text_h_scroll.set, wrap=NONE, undo=True)
        self.tl_text.pack(fill=BOTH, expand=True)
        setup_text_widget(self.tl_text)
        self.tl_text.bind('<Key>', self._on_key)
        self.tl_text.bind('<Button-1>', self._on_key)

        # config target language textbox scrollbars
        self.tl_text_v_scroll.config(command=self.tl_text.yview)
        self.tl_text_h_scroll.config(command=self.tl_text.xview)

        # progress bar
        self.progress = tk.IntVar(self, value=0)
        self.progress_bar = ttk.Progressbar(self, style='TProgressbar', variable=self.progress, maximum=1000)
        self.progress_bar.pack(fill=X, pady=(10, 0))

        # progress label
        self.progress_label = tk.Label(text=self.progress_text.format(source='auto', target='en', times=4, progress='0%', status='Stopped!'), anchor=E, bd=1, relief=SUNKEN)
        self.progress_label.pack(fill=X, side=BOTTOM)

        # menu
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        # print(self.cget('bg'))

        # file menu
        self.file_menu = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='Open File', command=self.open_text_file)
        self.file_menu.add_command(label='Save', command=self.save_text)
        self.file_menu.add_command(label='Save As', command=self.save_text_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', command=self.quit)

        # edit menu
        self.edit_menu = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label='Edit', menu=self.edit_menu)
        self.edit_menu.add_command(label='Undo', command=self.current_textbox.edit_undo)
        self.edit_menu.add_command(label='Redo', command=self.current_textbox.edit_redo)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Cut', command=self.current_textbox.cut)
        self.edit_menu.add_command(label='Copy', command=self.current_textbox.copy)
        self.edit_menu.add_command(label='Paste', command=self.current_textbox.paste)

        # about menu
        self.help_menu = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label='Help', menu=self.help_menu)
        self.help_menu.add_command(label='About', command=self.about)

    def _validate(self, P):
        return P.isdigit()

    def _on_key(self, event: tk.Event):
        if isinstance(event.widget, tk.Text):
            self.current_textbox.textbox = event.widget

    def start(self):
        # check if the source text box is empty
        if self.sl_text.get('1.0', END).replace('\n', ''):
            # disable button
            self.start_button.config(state=DISABLED)
            self.logger.debug('"Translate!" button disabled.')
            # get data and set configs
            self.logger.debug('Extracting data from sl_text, sl_combo, tl_combo and ts_times_spin fields...')
            text = self.sl_text.get("1.0", END)
            source = self.source_codes[self.sl_combo.get()]
            target = self.target_codes[self.tl_combo.get()]
            times = int(self.ts_times_spin.get())
            codes = cycle(self.target_codes.values())
            self.data = {'text': text, 'source': source, 'target': target, 'times': times, 'codes': codes}
            self.logger.debug('Data successfully extracted from sl_text, sl_combo, tl_combo and ts_times_spin fields.')
            # set progress bar
            self.progress.set(0)
            self.progress_label.config(text=self.progress_text.format(source=source, target=target, times=times, progress='0.00%', status='Connecting...'))
            # connect to the internet
            self.logger.info('Connecting to the internet...')
            process, parent_conn = function_async(check_internet_connection)
            self.after(1000, self.wait_process, 0, 30, process, parent_conn, self.on_function_finished)
        else:
            self.logger.warning('Source text box is empty!')
            messagebox.showwarning('Warning', 'Source text box is empty!')

    def wait_process(self, count: int, timeout: int, process: Process, parent_conn: Connection, callback: Callable):
        count += 1
        if count >= timeout:
            if process.is_alive():
                process.terminate()
                process.join()
                self.after(0, callback, None)
                return

        if parent_conn.poll():
            success, elapsed_time = parent_conn.recv()
            if success:
                self.after(0, callback, elapsed_time)
            else:
                self.after(0, callback, None)
        else:
            self.after(1000, self.wait_process, count, timeout, process, parent_conn, callback)

    def on_function_finished(self, elapsed_time: float | None):
        if elapsed_time is None:
            self.logger.error('Unable to connect to the Internet.')
            messagebox.showerror("Error", "Unable to connect to the Internet.")
            self.start_button.config(state=NORMAL)
            self.logger.debug('"Translate!" button enabled.')
            self.progress_label.config(text=self.progress_text.format(source=self.data['source'], target=self.data['target'], times=self.data['times'], progress='0.00%', status='Stopped!'))
        else:
            self.logger.debug(f"Internet connection checked in {elapsed_time:.2f} seconds.")
            self.logger.info('Internet connected!')
            self.translate()
    
    def translate(self):
        # start process
        self.logger.info(f'Translating the text {self.data['times']} times...')
        process = Process(target=nxt, args=(*self.data.values(),), kwargs={'bucket': self.bucket}, daemon=True)
        process.start()
        # set progress bar
        self.progress.set(0)
        self.progress_label.config(text=self.progress_text.format(source=self.data['source'], target=self.data['target'], times=self.data['times'], progress='0.00%', status='Running...'))
        self.after(500, self.update_status, process)
    
    def update_status(self, process: Process):
        update_again = True
        try:
            response: dict[str, str | None] = self.bucket.get_nowait()
            self.logger.info(f'Progress: {response['progress']:>7}    Status: {response['status']}')
            self.progress.set(int(float(response['progress'][:-1]) * 10))
            self.progress_label.config(text=self.progress_text.format(source=self.data['source'], target=self.data['target'], times=self.data['times'], progress=response['progress'], status=response['status']))
            if response['status'] == 'Complete!':
                self.logger.info('Process completed!')
                self.logger.debug('Sending result to tl_text field...')
                self.tl_text.delete("1.0", END)
                self.tl_text.insert("1.0", response['text'])
                self.logger.debug('Result sent successfully!')
                self.start_button.config(state=NORMAL)
                self.logger.debug('"Translate!" button enabled.')
                update_again = False
            elif response['status'] == 'Stopped!':
                self.logger.info('Process stopped!')
                if response.get('is_error', False):
                    if response.get('unusual_error', False):
                        crash_folder = find_data_paths('crashes')
                        if not os.path.exists(crash_folder):
                            os.makedirs(crash_folder, exist_ok=True)
                        filename = f'crash-{datetime.now().strftime('%Y%m%d%H%M%S')}.txt'
                        with open(os.path.join(crash_folder, filename), 'wt', encoding='utf-8') as file:
                            file.write(response['unusual_error'])
                        self.logger.critical(f'Unknown error! Check the "{filename}" file for more details.')
                        messagebox.showerror("Error", f'Unknown error! Check the "{filename}" file for more details.')
                    else:
                        self.logger.error('Unable to connect to the Internet.')
                        messagebox.showerror("Error", "Unable to connect to the Internet.")
                self.start_button.config(state=NORMAL)
                self.logger.debug('"Translate!" button enabled.')
                update_again = False
        except Empty:
            pass
        if update_again:
            self.after(500, self.update_status, process)

    def paste_text(self):
        try:
            self.logger.info('Pasting text...')
            text = pyperclip.paste()
            self.sl_text.delete('1.0', END)
            self.sl_text.insert('1.0', text)
            self.logger.info('Text pasted successfully!')
        except pyperclip.PyperclipException as err:
            self.logger.error('Copy/paste mechanism missing')
            messagebox.showerror('Copy/paste mechanism missing', str(err))
    
    def open_text_file(self):
        self.logger.info('Opening a text file and getting its content...')
        filename = filedialog.askopenfilename(defaultextension='.txt', filetypes=(('Text Files', '.txt',),), initialdir=f'/home/{getpass.getuser()}/Documentos', title='Open text file')
        if filename:
            with open(filename, 'rt', encoding='utf-8') as file:
                text = file.read()
            self.sl_text.delete('1.0', END)
            self.sl_text.insert('1.0', text)
            self.logger.info('Text file content obtained successfully!')
        else:
            self.logger.warning('No text file was opened.')
        
    def swap_langs(self):
        self.logger.info('Swapping languages...')
        sl_lang = self.sl_combo.get()
        if sl_lang != self.source_langs['auto']:
            tl_lang = self.tl_combo.get()
            self.sl_combo.delete(0, END)
            self.tl_combo.delete(0, END)
            self.sl_combo.insert(0, tl_lang)
            self.tl_combo.insert(0, sl_lang)
            self.logger.info('Languages swapped successfully!')
        else:
            self.logger.warning('You can\'t swap languages.')

    def copy_text(self):
        try:
            self.logger.info('Copying text...')
            text = self.tl_text.get('1.0', END)
            pyperclip.copy(text)
            self.logger.info('Text copied successfully!')
        except pyperclip.PyperclipException as err:
            self.logger.error('Copy/paste mechanism missing')
            messagebox.showerror('Copy/paste mechanism missing', str(err))
    
    def save_text(self):
        if self.filename:
            self.logger.info(f'Saving the content to the {self.filename} file...')
            with open(self.filename, 'wt', encoding='utf-8') as file:
                file.write(self.tl_text.get('1.0', END))
            self.logger.info('Text file saved successfully!')
        else:
            self.save_text_as()

    def save_text_as(self):
        self.logger.info('Opening the directory and saving the content to a text file...')
        filename = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=(('Text Files', '.txt',),), initialdir=f'/home/{getpass.getuser()}/Documentos', initialfile='output.txt', title='Save text file')
        if filename:
            with open(filename, 'wt', encoding='utf-8') as file:
                file.write(self.tl_text.get('1.0', END))
            self.filename = filename
            self.logger.info('Text file saved successfully!')
        else:
            self.logger.warning('No text file was chosen.')

    def about(self):
        def close_window():
            top.grab_release()
            top.destroy()

        top = tk.Toplevel(self)
        top.title('About N-Times Translator')
        top.resizable(False, False)
        top.transient(self)
        if os.name == 'nt':
            top.iconbitmap('nxt.ico')
        else:
            top.iconphoto(True, self.icon)
        width = 400
        height = 300
        monitor_width = self.winfo_width()
        monitor_height = self.winfo_height()
        top.geometry(f'{width}x{height}+{self.winfo_x() + ((monitor_width - width) // 2)}+{self.winfo_y() + ((monitor_height - height) // 2)}')

        # frame
        frame = tk.Frame(top)
        frame.pack(pady=20)

        # icon
        icon_img = ImageTk.PhotoImage(Image.open('nxt.png').resize((60, 60), reducing_gap=1.0))
        icon = tk.Label(frame, image=icon_img)
        icon.grid(row=0, column=0)

        # title
        title = tk.Label(frame, text='N-Times Translator', font=('Helvetica', 20, 'bold'))
        title.grid(row=0, column=1, pady=(8, 0), padx=(8, 0))

        # description
        description_text = \
'''N-Times Translator is a free and open source program
that takes a text in any language, sends it through
Google Translate a bunch of times, and then outputs
it in any language.'''
        description = tk.Label(top, text=description_text, justify=LEFT)
        description.pack()

        # second frame
        second_frame = tk.Frame(top)
        second_frame.pack(fill=X, pady=(20, 0), padx=(32, 0))

        # dev credit
        dev_title1 = tk.Label(second_frame, text='Developed by', font=('Helvetica', 10, 'bold'), justify=LEFT)
        dev_title1.grid(row=0, column=0, sticky=W)
        dev_title2 = tk.Label(second_frame, text='Danillo de Paula Silveira Sousa', font=('Helvetica', 10, 'underline'), fg='blue', cursor='hand2', justify=LEFT)
        dev_title2.grid(row=0, column=1)
        dev_title2.bind('<Button-1>', lambda e: webbrowser.open('https://github.com/danillo-de-paula-ss'))
        ToolTip(dev_title2, 'Click to open my GitHub', delay=0.5)

        # button
        ok_btn = tk.Button(top, text='OK', width=8, command=close_window)
        ok_btn.pack(side=BOTTOM, pady=(0, 10))

        top.grab_set()
        top.mainloop()

if __name__ == '__main__':
    if os.name == 'nt':
        freeze_support() # On Windows calling this function is necessary.
    app = App()
    app.mainloop()
