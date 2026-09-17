"""Sayfa 'silme' (Faz 4) - aslinda KALICI SILME degil, arsivleme.

Kullanicinin yanlislikla bir sayfayi kaybetmesini onlemek icin, silinen
sayfa '_deleted_pages/<sayfa>_<tarih_saat>/' altina (varsa otomatik yedek
klasoruyle birlikte) tasinir. Hicbir dosya gercekten silinmez; geri almak
icin o klasordeki .txt dosyasi DATA_DIR'in kokune elle geri tasinabilir.
"""
import os
import shutil
import time

from .backups import backup_dir_for_page

DELETED_PAGES_SUBDIR = "_deleted_pages"


def archived_pages_dir(data_dir):
    return os.path.join(data_dir, DELETED_PAGES_SUBDIR)


def archive_page(data_dir, page_name):
    """Sayfanin .txt dosyasini (ve varsa otomatik yedek klasorunu)
    _deleted_pages altina tasir. Basariliysa hedef klasor yolunu, sayfa
    dosyasi zaten yoksa None dondurur."""
    src_file = os.path.join(data_dir, f"{page_name}.txt")
    if not os.path.exists(src_file):
        return None

    stamp = time.strftime("%Y%m%d_%H%M%S")
    dest_dir = os.path.join(archived_pages_dir(data_dir), f"{page_name}_{stamp}")
    os.makedirs(dest_dir, exist_ok=True)

    shutil.move(src_file, os.path.join(dest_dir, f"{page_name}.txt"))

    backups_src = backup_dir_for_page(data_dir, page_name)
    if os.path.exists(backups_src):
        shutil.move(backups_src, os.path.join(dest_dir, "_backups"))

    return dest_dir
