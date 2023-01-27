import os
from cx_Freeze import setup, Executable

path = os.path.dirname(__file__) + os.sep
# O que deve ser incluído na pasta final
FILES = [path + 'nxt.ico']
INCLUDES = ['traceback', 'os', 'sys']
PACKAGES = ['googletrans2']
EXCLUDES = ['tkinter', 'googletrans']

# Saída de arquivos
config = Executable(
    script=path + 'nxt.py',
    icon=path + 'nxt.ico'
)

# Configurar o cx-freeze (detalhes do programa)
setup(
    name='N-Times Translator',
    version='1.0.1',
    description='This program translates a text n-times',
    author='DanilloEXE',
    options={'build_exe': {'include_files': FILES,
                           'packages': PACKAGES,
                           'includes': INCLUDES,
                           'excludes': EXCLUDES}},
    executables=[config]
)
