"""Sayfa secici (combobox), sayfa olusturma/yeniden adlandirma/gecis.

Orijinal setup_gui() icindeki combobox/'+ dugmesi kurulumu ve
get_pages/refresh_page_list/on_page_selected/rename_current_page/
create_new_page/switch_to_page/ensure_initial_file metodlari BIREBIR AYNI
davranisla buraya tasindi. Sadece isim sanitizasyonu ve sayfa listeleme
artik storage/pages.py'deki saf fonksiyonlari kullaniyor.
"""
import os
import tkinter as tk
from tkinter import ttk, Menu, messagebox

from ..storage.pages import list_pages, sanitize_page_name, is_reserved_name
from ..storage.backups import rename_backup_dir
from ..storage.page_delete import archive_page


class PageMixin:
    def setup_page_selector(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Modern.TCombobox',
            fieldbackground='#FFFFFF',
            background='#FFFFFF',
            foreground='#111827',
            bordercolor='#93C5FD',
            lightcolor='#93C5FD',
            darkcolor='#93C5FD',
            arrowcolor='#1E3A8A',
            padding=4
        )
        style.map('Modern.TCombobox',
            fieldbackground=[('readonly', '#FFFFFF')],
            background=[('readonly', '#FFFFFF')]
        )

        pages = self.get_pages()
        # Faz 4: kaydedilmis son sayfa hala varsa ondan devam edilir,
        # yoksa eski davranis (alfabetik ilk sayfa) korunur.
        initial_page = getattr(self, "_initial_page", None)
        if initial_page not in pages:
            initial_page = pages[0]
        self.page_var = tk.StringVar(value=initial_page)
        self.current_page = self.page_var.get()

        self.page_combo = ttk.Combobox(
            self.title_bar,
            textvariable=self.page_var,
            values=self.get_pages(),
            width=20,
            style='Modern.TCombobox',
            font=('Segoe UI', 9),
            postcommand=self.refresh_page_list
        )
        self.page_combo.pack(side="left", padx=(8, 4), pady=3)
        self.page_combo.bind("<<ComboboxSelected>>", self.on_page_selected)
        self.page_combo.bind("<Return>", self.rename_current_page)
        self.page_combo.bind("<Button-3>", self.show_page_context_menu)

        # Yeni Sayfa Ekle Butonu
        self.add_page_btn = tk.Label(
            self.title_bar,
            text="+",
            bg=self.RENK_UST,
            fg="#93C5FD",
            font=("Segoe UI", 12, "bold"),
            cursor="hand2",
            padx=6
        )
        self.add_page_btn.pack(side="left", pady=3)
        self.add_page_btn.bind("<Button-1>", self.create_new_page)
        self.add_page_btn.bind("<Enter>", lambda e: self.add_page_btn.config(fg="#FFFFFF"))
        self.add_page_btn.bind("<Leave>", lambda e: self.add_page_btn.config(fg="#93C5FD"))

    def ensure_initial_file(self):
        file_path = os.path.join(self.DATA_DIR, f"{self.current_page}.txt")
        if not os.path.exists(file_path):
            try:
                self._atomic_write(file_path, "")
            except Exception:
                self.logger.exception("Baslangic dosyasi olusturulamadi")

    def get_pages(self):
        return list_pages(self.DATA_DIR)

    def refresh_page_list(self):
        pages = self.get_pages()
        if self.current_page not in pages:
            pages.append(self.current_page)
        self.page_combo["values"] = sorted(list(set(pages)))

    def on_page_selected(self, event=None):
        selected = self.page_combo.get().strip()
        if selected and selected != self.current_page:
            self.switch_to_page(selected)

    def rename_current_page(self, event=None):
        new_name = sanitize_page_name(self.page_var.get().strip())

        if not new_name or new_name == self.current_page:
            self.page_var.set(self.current_page)
            self.text_area.focus_set()
            return "break"

        if is_reserved_name(new_name):
            self.show_temp_message("Bu isim kullanılamaz")
            self.page_var.set(self.current_page)
            self.text_area.focus_set()
            return "break"

        old_file = os.path.join(self.DATA_DIR, f"{self.current_page}.txt")
        new_file = os.path.join(self.DATA_DIR, f"{new_name}.txt")

        if os.path.exists(new_file):
            self.show_temp_message("Bu isimde sayfa var!")
            self.page_var.set(self.current_page)
            return "break"

        self.save_notes(self.current_page)
        try:
            if os.path.exists(old_file):
                os.rename(old_file, new_file)
        except Exception:
            self.logger.exception(f"Sayfa yeniden adlandirilamadi: {self.current_page} -> {new_name}")
            self.show_temp_message("Yeniden adlandırma başarısız")
            self.page_var.set(self.current_page)
            return "break"

        try:
            rename_backup_dir(self.DATA_DIR, self.current_page, new_name)
        except Exception:
            self.logger.exception(f"Yedek klasoru tasinamadi: {self.current_page} -> {new_name}")

        self.current_page = new_name
        self.page_var.set(new_name)
        self.refresh_page_list()
        self.show_temp_message("Yeniden Adlandırıldı")
        self.text_area.focus_set()
        return "break"

    def create_new_page(self, event=None):
        pages = self.get_pages()
        idx = 1
        while f"Sayfa {idx}" in pages:
            idx += 1
        new_page = f"Sayfa {idx}"
        self.switch_to_page(new_page)

    def switch_to_page(self, new_page):
        if self._save_job:
            self.app.after_cancel(self._save_job)
            self._save_job = None

        # Arama cubugu acikken sayfa degisirse eski eslesme konumlari
        # gecersiz kalir; sayfa gecisinde temiz baslamak icin kapatiyoruz.
        if getattr(self, "search_frame", None) is not None and self.search_frame.winfo_ismapped():
            self.close_search_bar()

        self.save_notes(self.current_page)
        self.current_page = new_page
        self.page_var.set(new_page)
        self.refresh_page_list()
        self.load_notes()
        self.text_area.focus_set()

    def show_page_context_menu(self, event=None):
        menu = Menu(self.app, tearoff=0)
        menu.add_command(label=f"'{self.current_page}' Sayfasını Sil", command=self.delete_current_page)
        menu.add_separator()
        menu.add_command(label="Kullanılmayan Görselleri Temizle", command=self.clean_unused_images)
        if event is not None:
            menu.post(event.x_root, event.y_root)
        return "break"

    def delete_current_page(self):
        onay = messagebox.askyesno(
            "Sayfayı Sil",
            f"'{self.current_page}' sayfasını silmek istediğinize emin misiniz?\n\n"
            "Kalıcı olarak silinmiyor; '_deleted_pages' klasörüne taşınacak, "
            "isterseniz oradan geri getirebilirsiniz.",
            parent=self.app,
        )
        if not onay:
            return

        if self._save_job:
            self.app.after_cancel(self._save_job)
            self._save_job = None

        page_to_delete = self.current_page
        self.save_notes(page_to_delete)

        try:
            archive_page(self.DATA_DIR, page_to_delete)
        except Exception:
            self.logger.exception(f"Sayfa arsivlenemedi: {page_to_delete}")
            self.show_temp_message("Silme başarısız")
            return

        remaining_pages = [p for p in self.get_pages() if p != page_to_delete]
        next_page = remaining_pages[0] if remaining_pages else "Sayfa 1"

        self.current_page = next_page
        self.page_var.set(next_page)
        self.ensure_initial_file()
        self.refresh_page_list()
        self.load_notes()
        self.text_area.focus_set()
        self.show_temp_message("Sayfa Arşivlendi")
