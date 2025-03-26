from typing import Iterator, Callable
from queue import Queue
import subprocess
from requests.exceptions import ConnectionError
import multiprocessing
from multiprocessing.connection import Connection
import time
import os

os.environ["translators_default_region"] = "EN"
import translators

def nxt(text: str, source: str, target: str, times: int, lang_codes: Iterator[str], *, bucket: Queue) -> str:
    try:
        for i in range(times):
            if i < times - 1:
                code = next(lang_codes)
                text = translators.translate_text(text, 'google', source, code)
                source = code
                bucket.put_nowait({'text': text, 'progress': f'{((i + 1) / times) * 100:.2f}%', 'status': 'Running...'})
            else:
                text = translators.translate_text(text, 'google', source, target)
                bucket.put_nowait({'text': text, 'progress': f'{((i + 1) / times) * 100:.2f}%', 'status': 'Complete!'})
    except ConnectionError:
        bucket.put_nowait({'text': None, 'progress': f'{((i) / times) * 100:.2f}%', 'status': 'Stopped!', 'is_error': True})
    except Exception as err:
        bucket.put_nowait({'text': None, 'progress': f'{((i) / times) * 100:.2f}%', 'status': 'Stopped!', 'is_error': True, 'unusual_error': str(err)})

def function_async(func: Callable):
    # start process
    parent_conn, child_conn = multiprocessing.Pipe()
    process = multiprocessing.Process(target=func, args=(child_conn,), daemon=True)
    process.start()
    return process, parent_conn

def check_internet_connection(pipe_conn: Connection):
    try:
        start_time = time.time()
        param = '-n' if os.name == 'nt' else '-c'
        subprocess.check_output(["ping", param, "1", "8.8.8.8"], stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        elapsed_time = time.time() - start_time
        pipe_conn.send((True, elapsed_time))
    except subprocess.CalledProcessError:
        pipe_conn.send((False, None))
    finally:
        pipe_conn.close()
