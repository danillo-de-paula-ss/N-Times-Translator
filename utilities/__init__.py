from typing import Iterator
from queue import Queue

class Translator:
    def __init__(self):
        try:
            import translators
            self.ts = translators
        except Exception:
            raise ConnectionError('Unable to connect the Internet.')

    def translate(self, source: str, target: str, text: str) -> str: 
        return self.ts.translate_text(text, 'google', source, target)

def nxt(translator: Translator, text: str, source: str, target: str, times: int, lang_codes: Iterator[str], *, bucket: Queue) -> str:
    for i in range(times):
        if i < times - 1:
            code = next(lang_codes)
            text = translator.translate(source, code, text)
            source = code
            bucket.put_nowait({'text': None, 'progress': f'{((i + 1) / times) * 100:.0f}%', 'status': 'Running...'})
        else:
            text = translator.translate(source, target, text)
            bucket.put_nowait({'text': text, 'progress': f'{((i + 1) / times) * 100:.0f}%', 'status': 'Complete!'})
