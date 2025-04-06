# Introduction
>
> N-Times Translator is a free and open source program that takes a text in any language, sends it through Google Translate a bunch of times, and then outputs it in any language.

## Table of Contents

* [Requirements](#-requirements)
* [Installation](#-installation)
* [Usage](#-usage)
* [To Do](#-to-do)
* [Attribution](#️-attribution)

## 💻 Requirements

* Python 3.x or newer

## 🚀 Installation

Clone this repository and cd into source repository:

```bash
git clone https://github.com/danillo-de-paula-ss/N-Times-Translator.git
cd N-Times-Translator
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

Note: Windows users can download an .exe file in [Releases](https://github.com/danillo-de-paula-ss/N-Times-Translator/releases) and place it in any location on their [PATH](https://en.wikipedia.org/wiki/PATH_%28variable%29) except for %SYSTEMROOT%\System32 (e.g. do not put in C:\Windows\System32). The .exe program file doesn't need Python installed.

## ☕ Usage

Inside the source repository, run the file `nxt.py` with this command:

```bash
python nxt.py
```

Then a window will open:

![Example of the program](examples/gui_example.png)

Select the source language in the combobox:

![Source Language Combobox](examples/animated/gui_1.gif)

Write the text you want to translate in the field below the combobox:

![Source Text Box](examples/animated/gui_2.gif)

Then select the target language in the other combobox:

![Target Language Combobox](examples/animated/gui_3.gif)

Choose the number of translations to be made in the spin field:

![Spin](examples/animated/gui_4.gif)

And finally click the "Translate!" button:

![Button](examples/animated/gui_5.gif)

Now just wait for the program to finish making all the translations and then it will print in the field below the target language combobox:

![Progress](examples/animated/gui_6.gif)

## 📋 To Do

* Add functionality to randomize languages ​​in the translation process.
* Add the functionality of changing the program language.
* Add Brazilian Portuguese to the program language.

## 🏆️ Attribution

* ![Paste](examples/buttons/paste_20x20.png) [Paste icons created by Freepik - Flaticon](https://www.flaticon.com/free-icons/paste)
* ![Open File](examples/buttons/open-file_20x20.png) [Open source icons created by Freepik - Flaticon](https://www.flaticon.com/free-icons/open-source)
* ![Copy](examples/buttons/copy_20x20.png) [Copy icons created by Ongicon - Flaticon](https://www.flaticon.com/free-icons/copy)
* ![Save](examples/buttons/diskette_20x20.png) [Save icons created by Freepik - Flaticon](https://www.flaticon.com/free-icons/save)
* ![Swap](examples/buttons/switch_20x20.png) [Swap icons created by Freepik - Flaticon](https://www.flaticon.com/free-icons/swap)
