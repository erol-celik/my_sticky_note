"""Hata gunlugu (log) kurulumu.

Daha once bircok yerde `except Exception: pass` ile sessizce yutulan
hatalar artik buradan kurulan logger araciligiyla bir dosyaya yaziliyor.
Kullanici deneyimi degismiyor (hatalar hala uygulamayi kesmiyor), sadece
artik teshis edilebilir hale geliyor.
"""
import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(base_dir):
    logger = logging.getLogger("StickyNote")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        try:
            log_path = os.path.join(base_dir, "sticky_note.log")
            handler = RotatingFileHandler(
                log_path, maxBytes=512_000, backupCount=2, encoding="utf-8"
            )
            handler.setFormatter(
                logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            )
            logger.addHandler(handler)
        except Exception:
            # Log dosyasi acilamazsa (izin/disk sorunu) uygulama yine de calismali
            logger.addHandler(logging.NullHandler())
    return logger
