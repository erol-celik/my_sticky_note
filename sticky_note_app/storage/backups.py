"""Hafif otomatik surum gecmisi (Faz 3).

Her kayitta DEGIL, makul araliklarla (varsayilan: 5 dakika) mevcut
(henuz uzerine yazilmamis) sayfa icerigini "my_sticky_data/_backups/<sayfa>/"
altina zaman damgali bir kopya olarak alir. Sayfa basina en fazla
MAX_BACKUPS_PER_PAGE kopya tutulur, fazlasi (sadece KENDI olusturdugumuz
eski yedekler) silinir.

Onemli: bu modul kullanicinin asil .txt/gorsel dosyalarina HICBIR ZAMAN
dokunmaz - sadece ek, ayri bir klasore kopya yazar. save_notes() icindeki
asil kaydetme islemi bu modulden BAGIMSIZ calisir; yedekleme basarisiz
olsa bile kaydetme etkilenmez (bkz. NotesMixin.save_notes).

"_backups" klasoru DATA_DIR'in koku degil bir ALT klasoru oldugu icin
storage.pages.list_pages() (sadece DATA_DIR kokunde *.txt arar) bunu
sayfa sanip listeye eklemez.
"""
import os
import shutil
import time

BACKUP_SUBDIR = "_backups"
MAX_BACKUPS_PER_PAGE = 10
MIN_BACKUP_INTERVAL_SECONDS = 300  # 5 dakika


def backup_dir_for_page(data_dir, page_name):
    return os.path.join(data_dir, BACKUP_SUBDIR, page_name)


def maybe_snapshot(data_dir, page_name, current_file_path, last_backup_times):
    """Yeterince zaman gectiyse (last_backup_times[page_name] kontrolu),
    diskteki MEVCUT (henuz kaydedilmemis yeni icerikle degismemis) halini
    yedekler. current_file_path henuz yoksa (ilk kayittan once) hicbir
    sey yapmaz - yedeklenecek bir "eski hal" yoktur."""
    if not os.path.exists(current_file_path):
        return

    now = time.time()
    last = last_backup_times.get(page_name, 0)
    if now - last < MIN_BACKUP_INTERVAL_SECONDS:
        return

    backup_dir = backup_dir_for_page(data_dir, page_name)
    os.makedirs(backup_dir, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(backup_dir, f"{stamp}.txt")
    if os.path.exists(dest):
        return  # ayni saniyede zaten yedek alinmis

    shutil.copyfile(current_file_path, dest)
    last_backup_times[page_name] = now
    _prune_old_backups(backup_dir)


def _prune_old_backups(backup_dir):
    files = sorted(f for f in os.listdir(backup_dir) if f.endswith(".txt"))
    excess = len(files) - MAX_BACKUPS_PER_PAGE
    for old_file in files[:max(0, excess)]:
        try:
            os.remove(os.path.join(backup_dir, old_file))
        except OSError:
            pass


def rename_backup_dir(data_dir, old_page_name, new_page_name):
    """Sayfa yeniden adlandirildiginda, o sayfanin yedek klasoru de
    (varsa) yeni isimle eslessin diye tasinir. Yedek klasoru yoksa
    (hic yedek alinmamissa) hicbir sey yapmaz."""
    old_dir = backup_dir_for_page(data_dir, old_page_name)
    new_dir = backup_dir_for_page(data_dir, new_page_name)
    if os.path.exists(old_dir) and not os.path.exists(new_dir):
        os.rename(old_dir, new_dir)
