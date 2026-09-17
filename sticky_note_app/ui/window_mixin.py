"""Pencere govdesi: baslik cubugu, kapatma dugmesi, surukleme, yeniden
boyutlandirma. Sayfa secici (combobox) ve metin alani kurulumu kendi
mixin'lerine devredildi (setup_page_selector / setup_text_area), ama
cagirilma sirasi orijinal setup_gui() ile BIREBIR AYNI korundu.
"""
import tkinter as tk

from ..storage.settings import save_settings


class WindowMixin:
    def setup_gui(self):
        self.app = tk.Tk()
        self.app.title("My Sticky Note")

        self.app.overrideredirect(True)
        self.app.attributes("-topmost", True)
        self.app.attributes("-alpha", 0.95)
        # Faz 4: kaydedilmis konum/boyut varsa geri yuklenir, yoksa eski
        # sabit varsayilan kullanilir.
        self.app.geometry(getattr(self, "_initial_geometry", "560x420+150+120"))
        self.app.configure(bg=self.RENK_ALT)

        # Baslik Cubugu
        self.title_bar = tk.Frame(self.app, bg=self.RENK_UST, relief="flat", bd=0, height=32)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.do_drag)

        # Kapatma Butonu
        self.close_button = tk.Label(
            self.title_bar,
            text="✕",
            bg=self.RENK_UST,
            fg="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            padx=10
        )
        self.close_button.pack(side="right", fill="y")
        self.close_button.bind("<Button-1>", self.close_app)
        self.close_button.bind("<Enter>", lambda e: self.close_button.config(bg="#EF4444", fg="#FFFFFF"))
        self.close_button.bind("<Leave>", lambda e: self.close_button.config(bg=self.RENK_UST, fg="#FFFFFF"))

        # Bilgi Mesaji
        self.save_label = tk.Label(
            self.title_bar,
            text="",
            bg=self.RENK_UST,
            fg="#10B981",
            font=("Segoe UI", 9, "bold")
        )
        self.save_label.pack(side="right", padx=8)

        self.setup_page_selector()   # PageMixin (combobox + '+' dugmesi)
        self.setup_text_area()       # TextEditorMixin (metin alani + kisayollar)
        self.setup_search_bar()      # SearchMixin (Ctrl+F, henuz gorunmez)

        # Boyutlandirma Tutamaci
        self.resize_grip = tk.Label(
            self.app,
            text="◢",
            bg=self.RENK_ALT,
            fg="#94A3B8",
            font=("Segoe UI", 12),
            cursor="bottom_right_corner",
        )
        self.resize_grip.place(relx=1.0, rely=1.0, anchor="se")
        self.resize_grip.bind("<Button-1>", self.start_resize)
        self.resize_grip.bind("<B1-Motion>", self.do_resize)

    def start_drag(self, event):
        self.app.x = event.x
        self.app.y = event.y

    def do_drag(self, event):
        deltax = event.x - self.app.x
        deltay = event.y - self.app.y
        x = self.app.winfo_x() + deltax
        y = self.app.winfo_y() + deltay
        self.app.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self.app.start_x = event.x_root
        self.app.start_y = event.y_root
        self.app.start_w = self.app.winfo_width()
        self.app.start_h = self.app.winfo_height()

    def do_resize(self, event):
        new_w = max(350, self.app.start_w + (event.x_root - self.app.start_x))
        new_h = max(250, self.app.start_h + (event.y_root - self.app.start_y))
        self.app.geometry(f"{new_w}x{new_h}")

    def close_app(self, event=None):
        self.save_notes()
        try:
            save_settings(self.DATA_DIR, {
                "geometry": self.app.geometry(),
                "zoom_level": self.zoom_level,
                "last_page": self.current_page,
            })
        except Exception:
            self.logger.exception("Ayarlar kaydedilemedi")
        self.app.destroy()
