# N-Times Translator
from googletrans2 import Translator, LANGCODES
from datetime import datetime
import traceback
import os
import sys


# Find path
def find_data_file(filename):
    if getattr(sys, "frozen", False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir, filename)


# Create a header
def header_and_input(ipt='', type='str'):
    print('\033[34mN-Times Translator\033[m')
    if type == 'int':
        while True:
            try:
                rt = int(input(ipt))
                break
            except:
                print('\033[31mPlease enter integers only.\033[m')
    elif type == 'natural':
        while True:
            try:
                rt = int(input(ipt))
                if rt >= 0:
                    break
                else:
                    print('\033[31mPlease enter natural numbers only.\033[m')
            except:
                print('\033[31mPlease enter natural numbers only.\033[m')
    elif type == 'path':
        while True:
            rt = input(ipt)
            # Check if the path exits
            if os.path.exists(find_data_file(rt)) and rt != '':
                break
            else:
                print('\033[31mPlease enter a valid path.\033[m')
    elif type == 'checklist':
        while True:
            rt = input(ipt)
            if rt in LANGCODES.values():
                break
            else:
                print('\033[31mPlease enter a valid language code.\033[m')
    else:
        rt = input(ipt)
    os.system('cls')
    return rt


# defining variables
os.system('cls')
translator = Translator()
languages = list(LANGCODES.values())
path = header_and_input('text file path: ', 'path')
sl = header_and_input('source: ', 'checklist')
tli = header_and_input('destiny: ', 'checklist')
amount = header_and_input('amount: ', 'natural')
count = 0
attempts = 0

# opening the file and extracting the datas
with open(path, 'rt', encoding='utf-8') as file:
    text = ""
    for line in file:
        text += line

# doing the translation n times
print('\033[34mN-Times Translator\033[m\n')
start_time = datetime.now()
for x in range(amount + 1):
    if count >= len(languages):
        count = 0
    elapsed_time = datetime.now() - start_time
    progress = round((x / amount if amount > 0 else 1) * 100, 2)
    progress_bar = f'\033[A[{"=" * int(progress / 2):<50}] \033[36m{progress:>6.2f}%\033[m of {amount} in \033[33m{str(elapsed_time)[2:7]}\033[m'
    print(progress_bar)
    if x == amount:
        tl = tli
    else:
        tl = languages[count]
    texts = [""]
    key = 0
    for line in text.split('\n'):
        if len(texts[key]) + len(line[:1000]) > 4000:
            texts.append("")
            key += 1
        if len(line) > 1000:
            texts[key] += line[:1000] + '\n'
        else:
            texts[key] += line + '\n'
    while True:
        try:
            text = ""
            for k, v in enumerate(texts, start=1):
                if v != "":
                    text += translator.translate(v, src=sl, dest=tl).text
                    if k < len(texts):
                        text += '\n'
            attempts = 0
            break
        except Exception as err:
            if err is not KeyboardInterrupt:
                attempts += 1
                exc_type, exc_value, exc_tb = sys.exc_info()
                tb = traceback.TracebackException(exc_type,
                                                  exc_value,
                                                  exc_tb)
                tb_txt = "".join(tb.format_exception_only())
                print(f'\033[A{tb_txt[:-1]}. Retrying ({attempts} of 10)...' +
                      ' ' * 50)
                print(progress_bar)
                if attempts >= 10:
                    print('\033[A\033[31mERROR:\033[m' +
                          f'{tb_txt[tb_txt.find(":") + 1:-1]}' +
                          ' ' * 50)
                    input('Press enter to close...')
                    break
            else:
                break
    if attempts >= 10:
        break
    sl = tl
    count += 1

if attempts < 10:
    # save the translation in a .txt file
    print('Saving in the file "result.txt"...')
    with open(find_data_file('result.txt'), 'wt', encoding='utf-8') as save_file:
        save_file.write(text)
    print('Complete!')
    input('Press enter to close...')
