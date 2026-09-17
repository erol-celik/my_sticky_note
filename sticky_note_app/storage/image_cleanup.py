"""Kullanilmayan gorsel temizligi (Faz 4).

Hicbir sayfada (aktif ya da arsivlenmis/silinmis) artik referans
verilmeyen gorseller SILINMEZ; bunun yerine 'images/_unused/' klasorune
tasinir. Boylece yanlislikla hala ihtiyac duyulan bir gorsel varsa elle
geri getirilebilir.

Not: otomatik surum yedekleri (_backups/) taranmiyor - eski bir yedekte
gecen ama guncel sayfada artik olmayan bir gorsel de "kullanilmiyor"
sayilir. Bu bilinen/kabul edilmis bir sinirlama (bkz. kullaniciya verilen
aciklama).
"""
import os
import shutil

from .note_format import parse_segments
from .page_delete import DELETED_PAGES_SUBDIR

UNUSED_SUBDIR = "_unused"


def find_referenced_images(data_dir):
    """DATA_DIR kokundeki tum *.txt sayfalarini VE _deleted_pages altinda
    arsivlenmis sayfalari tarayip referans verilen gorsel dosya adlarini
    bir kume olarak dondurur."""
    referenced = set()
    if not os.path.exists(data_dir):
        return referenced

    txt_paths = []
    for fname in os.listdir(data_dir):
        fpath = os.path.join(data_dir, fname)
        if fname.endswith(".txt") and os.path.isfile(fpath):
            txt_paths.append(fpath)

    deleted_dir = os.path.join(data_dir, DELETED_PAGES_SUBDIR)
    if os.path.isdir(deleted_dir):
        for root, _dirs, files in os.walk(deleted_dir):
            for fname in files:
                if fname.endswith(".txt"):
                    txt_paths.append(os.path.join(root, fname))

    for fpath in txt_paths:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue
        for segment in parse_segments(content):
            if segment[0] == "image":
                referenced.add(segment[1])

    return referenced


def move_unused_images(img_dir, referenced_filenames):
    """img_dir icindeki, referenced_filenames kumesinde olmayan gorselleri
    'img_dir/_unused/' altina TASIR (silmez). Tasinan dosya adlarinin
    listesini dondurur."""
    if not os.path.exists(img_dir):
        return []

    unused_dir = os.path.join(img_dir, UNUSED_SUBDIR)
    moved = []
    for fname in os.listdir(img_dir):
        fpath = os.path.join(img_dir, fname)
        if not os.path.isfile(fpath):
            continue  # _unused klasorunun kendisi dahil, klasorleri atla
        if fname in referenced_filenames:
            continue
        os.makedirs(unused_dir, exist_ok=True)
        dest = os.path.join(unused_dir, fname)
        if os.path.exists(dest):
            continue  # zaten tasinmis
        shutil.move(fpath, dest)
        moved.append(fname)
    return moved
