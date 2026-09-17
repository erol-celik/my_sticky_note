"""Sayfa (.txt dosyasi) listeleme ve isim dogrulama mantigi.

Orijinal tek-dosyalik uygulamada get_pages() ve rename_current_page()
icine gomulmus sanitizasyon kodu buraya, Tkinter'dan bagimsiz saf
fonksiyonlar olarak tasindi. Davranis BIREBIR AYNI.
"""
import os

# Windows'ta dosya adi olarak kullanilamayan ayrilmis cihaz isimleri
WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}
MAX_PAGE_NAME_LENGTH = 80
DEFAULT_PAGE = "Sayfa 1"


def list_pages(data_dir):
    if not os.path.exists(data_dir):
        return [DEFAULT_PAGE]
    pages = sorted([
        f.replace(".txt", "")
        for f in os.listdir(data_dir)
        if f.endswith(".txt")
    ])
    if not pages:
        return [DEFAULT_PAGE]
    if DEFAULT_PAGE not in pages:
        pages.insert(0, DEFAULT_PAGE)
    return pages


def sanitize_page_name(raw_name):
    """Sayfa adi olarak izin verilen karakterleri filtreler, Windows'ta
    dosya adi sonunda olamayacak nokta/bosluklari kirpar ve asiri uzun
    isimleri kisaltir."""
    name = "".join(c for c in raw_name if c.isalnum() or c in " _-")
    name = name.strip(" .")
    if len(name) > MAX_PAGE_NAME_LENGTH:
        name = name[:MAX_PAGE_NAME_LENGTH].strip(" .")
    return name


def is_reserved_name(name):
    return name.upper() in WINDOWS_RESERVED_NAMES
