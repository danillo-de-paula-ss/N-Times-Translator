# N-Times Translator
from googletrans2 import Translator, LANGCODES
from datetime import datetime
from random import choices
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
def header():
    return '\033[1;36m' + ' N-Times Translator '.center(os.get_terminal_size().columns, '-') + '\033[m'

# Inputs
def header_and_input(prompt='', type='string'):
    print(header())
    if type == 'integer':
        while True:
            try:
                ans = int(input(prompt))
                break
            except ValueError:
                print('\033[31mPlease enter integers only.\033[m')
    elif type == 'natural':
        while True:
            try:
                ans = int(input(prompt))
                if ans >= 0:
                    break
                else:
                    print('\033[31mPlease enter natural numbers only.\033[m')
            except ValueError:
                print('\033[31mPlease enter natural numbers only.\033[m')
    elif type == 'path':
        while True:
            ans = input(prompt)
            # Check if the path exits
            if os.path.exists(find_data_file(ans)) and ans != '':
                break
            else:
                print('\033[31mPlease enter a valid path.\033[m')
    elif type == 'checklist':
        print('\033[35mOpen \033[4mlanguage_codes.txt\033[0;35m to see a list of available language codes\033[m')
        while True:
            ans = input(prompt)
            if ans in LANGCODES.values():
                break
            else:
                print('\033[31mPlease enter a valid language code.\033[m')
    elif type == 'choice':
        while True:
            ans = input(prompt)
            if ans == 'y' or ans == 'n':
                break
            else:
                print('\033[31mPlease answer y or n.\033[m')
    else:
        ans = input(prompt)
    os.system('cls')
    return ans

def main():
    # defining variables
    os.system('cls')
    translator = Translator()
    languages = list(LANGCODES.values())
    path = header_and_input('Text File Path: ', 'path')
    sl = header_and_input('Source: ', 'checklist')
    tli = header_and_input('Destiny: ', 'checklist')
    amount = header_and_input('Amount: ', 'natural')
    randomize_languages = header_and_input('Randomly translate? (y/n) ', 'choice')
    if randomize_languages == 'y':
        languages = choices(languages, k=len(languages))
    count = 0
    attempts = 0

    # opening the file and extracting the datas
    with open(path, 'rt', encoding='utf-8') as file:
        text = "".join(file.readlines())

    # counting the empty lines at the beginning and end
    lines = text.split('\n')
    initial_empty_lines = 0
    for v in lines:
        if v != '':
            break
        initial_empty_lines += 1
    last_empty_lines = 0
    for v in reversed(lines):
        if v != '':
            break
        last_empty_lines += 1

    # doing the translation n times
    print(header() + '\n')
    initial_time = datetime.now()
    for x in range(amount + 1):
        if count >= len(languages):
            count = 0
        elapsed_time = datetime.now() - initial_time
        progress = round((x / amount if amount > 0 else 1) * 100, 2)
        progress_bar = f'\033[A[{"=" * int(progress / 2):<50}] \033[36m{progress:>6.2f}%\033[m of {amount} in \033[33m{str(elapsed_time)[2:7]}\033[m' + ' ' * 30
        print(progress_bar)
        if x == amount:
            tl = tli
        else:
            tl = languages[count]
        key = 0
        texts = [""]
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
                    tb = traceback.TracebackException(exc_type, exc_value, exc_tb)
                    tb_txt = "".join(tb.format_exception_only())
                    print(f'\033[A{tb_txt[:-1]}. Retrying ({attempts} of 10)...' + ' ' * 50)
                    print(progress_bar)
                    if attempts >= 10:
                        print('\033[A\033[31mERROR:\033[m' + f'{tb_txt[tb_txt.find(":") + 1:-1]}' + ' ' * 50)
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
            save_file.write('\n' * initial_empty_lines + text + '\n' * last_empty_lines)
        print('Complete!')
        input('Press enter to close...')


if __name__ == '__main__':
    main()
