"""StickyNoteApp - butun mixin'leri bir araya getiren ana sinif.

base_dir DISARIDAN parametre olarak aliniyor (giris noktasi my_sticky_note.py
tarafindan hesaplanip geciriliyor). Bunun nedeni: orijinal tek-dosyalik
uygulamada base_dir, __file__'in (yani my_sticky_note.py'nin) bulundugu
klasordu. Kod modullere bolununce, eger bu hesaplama buraya (app.py'ye)
tasinsaydi, __file__ artik sticky_note_app/app.py'yi gosterecegi icin
BIR KLASOR YANLIS hesaplanip my_sticky_data/ klasoru proje kokunde degil
sticky_note_app/ altinda aranmaya baslardi - kullanicinin mevcut notlarina
erisim kaybi anlamina gelirdi. Bu riski tamamen ortadan kaldirmak icin
base_dir hesaplamasi TEK bir yerde (giris noktasinda) yapiliyor.
"""
import os

from .config import RENK_UST, RENK_ALT, YAZI_RENGI
from .logging_setup import setup_logging
from .storage.atomic_io import atomic_write
from .storage.settings import load_settings
from .ui.window_mixin import WindowMixin
from .ui.page_mixin import PageMixin
from .ui.text_editor_mixin import TextEditorMixin
from .ui.image_mixin import ImageMixin
from .ui.notes_mixin import NotesMixin
from .ui.hotkeys_mixin import HotkeysMixin
from .ui.search_mixin import SearchMixin


class StickyNoteApp(WindowMixin, PageMixin, TextEditorMixin, ImageMixin, NotesMixin, HotkeysMixin, SearchMixin):
    def __init__(self, base_dir):
        self.DATA_DIR = os.path.join(base_dir, "my_sticky_data")
        self.IMG_DIR = os.path.join(self.DATA_DIR, "images")
        os.makedirs(self.IMG_DIR, exist_ok=True)

        self.logger = setup_logging(base_dir)

        self.RENK_UST = RENK_UST
        self.RENK_ALT = RENK_ALT
        self.YAZI_RENGI = YAZI_RENGI

        # Kaydedilmis ayarlar (pencere konumu/boyutu, son sayfa, zoom) -
        # dosya yoksa/bozuksa guvenli varsayilanlar donuyor, uygulama asla
        # bu yuzden acilmayi reddetmiyor.
        saved_settings = load_settings(self.DATA_DIR)
        self._initial_geometry = saved_settings["geometry"]
        self._initial_page = saved_settings["last_page"]

        self.global_images = {}
        self.image_cache = {}
        self.image_info = {}
        self.current_page = "Sayfa 1"
        self.is_visible = True

        self.zoom_level = saved_settings["zoom_level"]
        self.base_font_size = 12
        self._save_job = None
        self._last_backup_times = {}  # {sayfa_adi: son_otomatik_yedek_zamani}

        self.setup_gui()
        self.apply_zoom(self.zoom_level)  # kaydedilmis zoom varsa geri yuklenir
        self.setup_hotkeys()
        self.ensure_initial_file()
        self.load_notes()

    def _atomic_write(self, path, content):
        atomic_write(path, content)

    def run(self):
        self.app.mainloop()
