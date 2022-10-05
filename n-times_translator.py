# N-Times Translator
from googletrans2 import Translator, LANGCODES
from time import sleep
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
    print('\033[34mN-times Translator\033[m')
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
            rt = find_data_file(input(ipt))
            # Check if the path exits
            if os.path.exists(rt):
                break
            else:
                print('\033[31mPlease enter a valid path.\033[m')
    else:
        rt = input(ipt)
    os.system('cls')
    return rt


# defining variables
os.system('cls')
translator = Translator()
languages = list(LANGCODES.values())
path = header_and_input('text file path: ', 'path')
sl = header_and_input('source: ')
tli = header_and_input('destiny: ')
amount = header_and_input('amount: ', 'natural')
count = 0
attempts = 0

# opening the file and extracting the data
with open(path, 'rt', encoding='utf-8') as file:
    text = ""
    for line in file:
        text += line

# doing the translation n times
print('\033[34mN-times Translator\033[m')
for x in range(amount + 1):
    if count >= len(languages):
        count = 0
    print(f'{round((x / amount if amount > 0 else 1) * 100, 2):.2f}%')
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
                if attempts > 1:
                    print("Attempts: ", attempts)
                else:
                    print("\nAttempts: ", attempts)
                exc_type, exc_value, exc_tb = sys.exc_info()
                tb = traceback.TracebackException(exc_type, exc_value, exc_tb)
                print(''.join(tb.format_exception_only()))
                if attempts >= 10:
                    print('\n', count, sl, tl)
                    raise Exception("Exceeded 10 attempts")
            else:
                break
    sl = tl
    count += 1

# save the translation in a .txt file
print('Saving in the file "result.txt"...')
with open(find_data_file('result.txt'), 'wt', encoding='utf-8') as save_file:
    save_file.write(text)
print('Complete!')
input('Press enter to close...')
