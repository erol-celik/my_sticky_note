"""Giris noktasi.

my_sticky_note.spec (PyInstaller) hala bu dosyayi referans aliyor, bu
yuzden dosya adi/konumu KORUNDU. Gercek uygulama kodu artik
sticky_note_app/ paketi altinda, ozellige gore modullere ayrilmis halde
duruyor (bkz. sticky_note_app/app.py ve altindaki storage/ , ui/ ,
platform_win/ paketleri).
"""
import os
import sys

from sticky_note_app.app import StickyNoteApp


def _resolve_base_dir():
    # Orijinal (tek dosyalik) uygulamayla BIREBIR AYNI mantik: PyInstaller
    # ile paketlenmisse .exe'nin bulundugu klasor, degilse bu script'in
    # bulundugu klasor baz alinir. my_sticky_data/ klasoru boylece her
    # zaman proje kokunde kalir.
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    app = StickyNoteApp(base_dir=_resolve_base_dir())
    app.run()
