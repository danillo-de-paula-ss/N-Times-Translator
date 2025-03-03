from typing import Iterator, Any
from queue import Queue
import traceback
from multiprocessing.connection import Connection
import time
import importlib

def import_module(pipe_conn, module_name):
    """Tenta importar um módulo e envia o resultado via Pipe."""
    try:
        start_time = time.time()
        module = importlib.import_module(module_name)
        elapsed_time = time.time() - start_time
        pipe_conn.send((True, module.__name__, elapsed_time))  # Envia o nome do módulo e o tempo gasto
    except Exception as e:
        pipe_conn.send((False, str(e), None))  # Envia erro
    finally:
        pipe_conn.close()

class Translator:
    def __init__(self):
        try:
            import translators
            self.ts = translators
        except Exception:
            raise ConnectionError('Unable to connect the Internet.')

    def translate(self, source: str, target: str, text: str) -> str: 
        return self.ts.translate_text(text, 'google', source, target)

def nxt(translator, text: str, source: str, target: str, times: int, lang_codes: Iterator[str], *, bucket: Queue) -> str:
    for i in range(times):
        if i < times - 1:
            code = next(lang_codes)
            text = translator.translate_text(text, 'google', source, code)
            source = code
            bucket.put_nowait({'text': None, 'progress': f'{((i + 1) / times) * 100:.0f}%', 'status': 'Running...'})
        else:
            text = translator.translate_text(text, 'google', source, target)
            bucket.put_nowait({'text': text, 'progress': f'{((i + 1) / times) * 100:.0f}%', 'status': 'Complete!'})
