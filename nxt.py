# N-Times Translator
import importlib.abc
import importlib.machinery
import importlib.metadata
import importlib.readers
import importlib.resources
import importlib.simple
import importlib.util
import logging.config
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.constants import *
import os
import json
from PIL import Image, ImageTk
from utilities import nxt, import_module
from itertools import cycle
import pyperclip
# import threading
# import queue
from multiprocessing import Process, Queue, Pipe
from multiprocess.queues import Empty
from multiprocess.connection import Connection
import importlib
from typing import Callable
import logging
from types import ModuleType

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

        ## set logger
        # create logger
        self.logger = logging.getLogger('main')
        self.logger.setLevel(logging.DEBUG)
        # console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        # formatter
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s', '%H:%M:%S')
        console_handler.setFormatter(console_formatter)
        # add the handlers to logger
        self.logger.addHandler(console_handler)

        # set configs
        ttk.Style().theme_use("clam")
        ttk.Style().configure('Style1.TButton', font=('Helvetica', 14))
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
        self.process = None
        self.bucket = Queue()
        self.data = {}
        self.progress_text = 'source: {source}, target: {target}, times: {times}, progress: {progress}, status: {status}' + ' ' * 4

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
        self.sl_label.grid(row=0, column=0, pady=10, sticky=EW)

        # source language combo
        self.sl_combo = ttk.Combobox(self.sl_frame, values=self.sl_names, font=('Helvetica', 12))
        self.sl_combo.set(self.sl_names[0])
        self.sl_combo.grid(row=1, column=0, pady=(0, 2), padx=(1, 0), ipady=7, sticky=EW)

        # paste text button
        self.paste_img = ImageTk.PhotoImage(Image.open('buttons/paste.png').resize((30, 30), reducing_gap=1.0))
        self.sl_paste_btn = ttk.Button(self.sl_frame, image=self.paste_img, padding=(0, 0), command=self.paste_text)
        self.sl_paste_btn.grid(row=1, column=1, pady=(0, 2), padx=4)

        # open file button
        self.open_file_img = ImageTk.PhotoImage(Image.open('buttons/open-file.png').resize((30, 30), reducing_gap=1.0))
        self.sl_open_file_btn = ttk.Button(self.sl_frame, image=self.open_file_img, padding=(0, 0), command=self.open_text_file)
        self.sl_open_file_btn.grid(row=1, column=2, pady=(0, 2))

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
        
        # switch languages config
        # switch languages button
        self.swap_img = ImageTk.PhotoImage(Image.open('buttons/switch.png').resize((40, 40), reducing_gap=1.0))
        self.swap_language_btn = ttk.Button(self.main_frame, text='Switch Languages', image=self.swap_img, padding=(0, 0), compound=TOP, style='Style1.TButton', command=self.swap_langs)
        self.swap_language_btn.grid(row=0, column=1, pady=(6, 0), ipadx=10, sticky=NS)

        # panel frame config
        # push element
        self.vpush1 = tk.Text(self.panel_frame, font='_ 1', bd=0, padx=0, pady=0, width=0, state=DISABLED, bg='#d9d9d9', highlightthickness=0)
        self.vpush1.pack(fill=Y, expand=True)

        # translation times frame
        self.ts_times_frame = tk.Frame(self.panel_frame)
        self.ts_times_frame.pack()

        # translation times label 1
        self.ts_times_label_1 = ttk.Label(self.ts_times_frame, text='Translate', anchor=CENTER)
        self.ts_times_label_1.grid(row=0, column=0, ipadx=6, ipady=6)

        # translation times spin
        self.ts_times_spin = ttk.Spinbox(self.ts_times_frame, from_=1, to=1000, font=('Helvetica', 12), width=10)
        self.ts_times_spin.set(4)
        self.ts_times_spin.grid(row=0, column=1)

        # translation times label 2
        self.ts_times_label_2 = ttk.Label(self.ts_times_frame, text='times', anchor=CENTER)
        self.ts_times_label_2.grid(row=0, column=2, ipadx=6, ipady=6)

        # start button
        self.start_button = ttk.Button(self.panel_frame, text='Start Translation!', padding=(0, 0), style='Style2.TButton', command=lambda: self.import_module_async('translators', 5, self.on_import_finished))
        self.start_button.pack(pady=(10, 0), ipadx=8, ipady=8)

        # push element
        self.vpush2 = tk.Text(self.panel_frame, font='_ 1', bd=0, padx=0, pady=0, width=0, state=DISABLED, bg='#d9d9d9', highlightthickness=0)
        self.vpush2.pack(fill=Y, expand=True)

        # target frame config
        # target language label
        self.tl_label = tk.Label(self.tl_frame, text='Target Language', font=('Helvetica', 16, 'bold'))
        self.tl_label.grid(row=0, column=0, pady=10, sticky=EW)

        # target language combo
        self.tl_combo = ttk.Combobox(self.tl_frame, values=self.tl_names, font=('Helvetica', 12))
        self.tl_combo.set(self.tl_names[58])
        self.tl_combo.grid(row=1, column=0, pady=(0, 2), padx=(1, 0), ipady=7, sticky=EW)

        # copy text button
        self.copy_img = ImageTk.PhotoImage(Image.open('buttons/copy.png').resize((30, 30), reducing_gap=1.0))
        self.tl_copy_btn = ttk.Button(self.tl_frame, image=self.copy_img, padding=(0, 0), command=self.copy_text)
        self.tl_copy_btn.grid(row=1, column=1, pady=(0, 2), padx=4)

        # save text button
        self.save_text_img = ImageTk.PhotoImage(Image.open('buttons/diskette.png').resize((30, 30), reducing_gap=1.0))
        self.tl_save_text_btn = ttk.Button(self.tl_frame, image=self.save_text_img, padding=(0, 0), command=self.save_text_file)
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
        self.progress_label = tk.Label(text=self.progress_text.format(source='auto', target='en', times=4, progress='0%', status='Stopped!'), anchor=E, bd=1, relief=SUNKEN)
        self.progress_label.pack(fill=X, side=BOTTOM)

    def import_module_async(self, module_name: str, timeout: int, callback: Callable):
        # get data and set configs
        self.logger.debug('Extracting data from sl_text, sl_combo, tl_combo and ts_times_spin fields...')
        text = self.sl_text.get("1.0", END)
        source = self.source_codes[self.sl_combo.get()]
        target = self.target_codes[self.tl_combo.get()]
        times = int(self.ts_times_spin.get())
        codes = cycle(self.target_codes.values())
        self.data = {'text': text, 'source': source, 'target': target, 'times': times, 'codes': codes}
        self.logger.debug('Data successfully extracted from sl_text, sl_combo, tl_combo and ts_times_spin fields.')
        self.progress_label.config(text=self.progress_text.format(source=source, target=target, times=times, progress='0%', status='Connecting...'))
        self.start_button.config(state=DISABLED)
        self.logger.debug('Botão "Start Translation!" desabilitado.')
        # start process
        self.logger.debug('Iniciando processo de importação do módulo "translators"')
        parent_conn, child_conn = Pipe()
        process = Process(target=import_module, args=(child_conn, module_name), daemon=True)
        process.start()
        self.after(1000, self.wait_process, 0, timeout, process, parent_conn, callback)

    def wait_process(self, count: int, timeout: int, process: Process, parent_conn: Connection, callback: Callable):
        count += 1
        if count >= timeout:
            if process.is_alive():
                process.terminate()
                process.join()
                self.after(0, callback, None, f"Tempo limite excedido ({timeout}s)", None)
                return

            if parent_conn.poll():  # Se há dados no pipe
                success, result, elapsed_time = parent_conn.recv()
                if success:
                    self.after(0, callback, importlib.import_module(result), None, elapsed_time)
                else:
                    self.after(0, callback, None, result, None)
            else:
                self.after(0, callback, None, "Falha desconhecida ao importar o módulo.", None)
        else:
            self.after(1000, self.wait_process, count, timeout, process, parent_conn, callback)

    def on_import_finished(self, module: ModuleType, error: str, elapsed_time: float):
        """Callback chamado quando a importação terminar."""
        if error:
            messagebox.showerror("Erro", "Não foi possível conectar a internet.")
            print(f"Erro ao importar módulo:\n{error}")
            self.start_button.config(state=NORMAL)
            self.progress_label.config(text=self.progress_text.format(source=self.data['source'], target=self.data['target'], times=self.data['target'], progress='0%', status='Stopped!'))
        else:
            # messagebox.showinfo("Sucesso", f"Módulo '{module.__name__}' importado em {elapsed_time:.2f} segundos")
            print(f"Módulo '{module.__name__}' importado em {elapsed_time:.2f} segundos")
            self.start_translation(ts=module)
    
    def start_translation(self, ts):
        # start process
        process = Process(target=nxt, args=(ts, *self.data.values()), kwargs={'bucket': self.bucket}, daemon=True)
        process.start()
        self.progress_label.config(text=self.progress_text.format(source=self.data['source'], target=self.data['target'], times=self.data['target'], progress='0%', status='Running...'))
        self.after(500, self.update_status, process)
        # translations = ""
        # translations += f"{source_code} -> {code}\n"
        # translations += f"{source_code} -> {target_code}\n"
        # print(translations[:-1])
    
    def update_status(self, process: Process):
        update_again = True
        try:
            response: dict[str, str | None] = self.bucket.get_nowait()
            self.progress_label.config(text=self.progress_text.format(source=self.data['source'], target=self.data['target'], times=self.data['target'], progress=response['progress'], status=response['status']))
            if response['status'] == 'Complete!':
                self.tl_text.delete("1.0", END)
                self.tl_text.insert("1.0", response['text'])
                self.start_button.config(state=NORMAL)
                update_again = False
        except Empty:
            pass
        if update_again:
            self.after(500, self.update_status, process)

    def paste_text(self):
        try:
            text = pyperclip.paste()
            self.sl_text.delete('1.0', END)
            self.sl_text.insert('1.0', text)
        except pyperclip.PyperclipException as err:
            messagebox.showerror('Copy/paste mechanism missing', str(err))
    
    def open_text_file(self):
        filename = filedialog.askopenfilename(defaultextension='.txt', filetypes=(('Text Files', '.txt',),), initialdir='/home/danillo/Documentos', title='Open text file')
        if filename:
            with open(filename, 'rt', encoding='utf-8') as file:
                text = file.read()
            self.sl_text.delete('1.0', END)
            self.sl_text.insert('1.0', text)
        
    def swap_langs(self):
        sl_lang = self.sl_combo.get()
        if sl_lang != self.source_langs['auto']:
            tl_lang = self.tl_combo.get()
            self.sl_combo.delete(0, END)
            self.tl_combo.delete(0, END)
            self.sl_combo.insert(0, tl_lang)
            self.tl_combo.insert(0, sl_lang)

    def copy_text(self):
        try:
            text = self.tl_text.get('1.0', END)
            pyperclip.copy(text)
        except pyperclip.PyperclipException as err:
            messagebox.showerror('Copy/paste mechanism missing', str(err))
    
    def save_text_file(self):
        filename = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=(('Text Files', '.txt',),), initialdir='/home/danillo/Documentos', initialfile='output.txt', title='Save text file')
        if filename:
            with open(filename, 'wt', encoding='utf-8') as file:
                file.write(self.tl_text.get('1.0', END))

if __name__ == '__main__':
    app = App()
    app.mainloop()
