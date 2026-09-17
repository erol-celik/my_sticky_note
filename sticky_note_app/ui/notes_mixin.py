"""Sayfa yukleme/kaydetme ve gecici bilgi mesaji. Ayristirma/serilestirme
artik storage/note_format.py'deki saf fonksiyonlari kullaniyor; kaydetme
storage/atomic_io.py uzerinden atomik yapiliyor (self._atomic_write,
app.py'de tanimli). Davranis orijinal load_notes/save_notes ile BIREBIR
AYNI.
"""
import os

from ..storage.note_format import parse_segments, serialize_dump
from ..storage.backups import maybe_snapshot


class NotesMixin:
    def load_notes(self):
        self.text_area.delete("1.0", "end")
        self.global_images.clear()
        self.image_info.clear()
        # Sayfa gecisinde ham gorsel onbellegi de temizlenir; aksi halde
        # uzun oturumlarda tum sayfalarin gorselleri bellekte birikirdi.
        # Gerekirse diskten (IMG_DIR) tekrar yuklenir, veri kaybi olmaz.
        self.image_cache.clear()

        file_path = os.path.join(self.DATA_DIR, f"{self.current_page}.txt")
        if not os.path.exists(file_path):
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
        except Exception:
            self.logger.exception(f"Sayfa okunamadi: {self.current_page}")
            self.show_temp_message("Sayfa okunamadı!")
            return

        for segment in parse_segments(content):
            if segment[0] == "image":
                _, filename, scale = segment
                img_path = os.path.join(self.IMG_DIR, filename)
                if os.path.exists(img_path):
                    self._insert_image(img_path, filename, scale, at_index="end-1c")
            else:
                _, part = segment
                self.text_area.insert("end-1c", part)

        self.highlight_links()
        self.text_area.edit_reset()

    def show_temp_message(self, text):
        self.save_label.config(text=text)
        self.app.after(1500, lambda: self.save_label.config(text=""))

    def save_notes_with_message(self, event=None):
        self.save_notes()
        self.highlight_links()
        self.show_temp_message("Kaydedildi")

    def save_notes(self, target_page=None):
        page_to_save = target_page if target_page else self.current_page
        file_path = os.path.join(self.DATA_DIR, f"{page_to_save}.txt")

        # Yeterince zaman gectiyse (varsayilan 5 dk), uzerine yazmadan ONCE
        # mevcut halini "_backups/" altina yedekler. Bu adim basarisiz olsa
        # bile asil kaydetme islemi asla etkilenmez (ayri try/except).
        try:
            maybe_snapshot(self.DATA_DIR, page_to_save, file_path, self._last_backup_times)
        except Exception:
            self.logger.exception(f"Otomatik surum yedegi alinamadi: {page_to_save}")

        # end-1c ile kalici bosluk birikmesi engellenir
        content = serialize_dump(self.text_area.dump("1.0", "end-1c"), self.image_info)

        try:
            self._atomic_write(file_path, content)
        except Exception:
            self.logger.exception(f"Sayfa kaydedilemedi: {page_to_save}")
            self.show_temp_message("Kaydetme hatası!")

    def auto_save_and_highlight(self):
        self.save_notes()
        self.highlight_links()
