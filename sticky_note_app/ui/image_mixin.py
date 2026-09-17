"""Gorsel ekleme/goruntuleme/yeniden boyutlandirma/silme ve panodan
yapistirma/kesme. Orijinal dosyadaki ilgili metodlarin BIREBIR AYNI
tasinmis hali. copy_image_to_clipboard artik ctypes/windll kodunu
platform_win/clipboard.py'den cagiriyor.
"""
import os
import shutil
import time
import tkinter as tk
from tkinter import Menu, filedialog, messagebox

from PIL import Image, ImageTk, ImageGrab

from ..platform_win.clipboard import copy_image_to_windows_clipboard
from ..storage.image_cleanup import find_referenced_images, move_unused_images


class ImageMixin:
    def _insert_image(self, img_path, filename, scale=1.0, at_index=None):
        if filename not in self.image_cache:
            try:
                self.image_cache[filename] = Image.open(img_path).convert("RGBA")
            except Exception:
                self.logger.exception(f"Gorsel acilamadi: {img_path}")
                return

        img = self.image_cache[filename]
        orig_width, orig_height = img.size

        max_size = 450
        if orig_width > max_size or orig_height > max_size:
            ratio = min(max_size / orig_width, max_size / orig_height)
            base_width = int(orig_width * ratio)
            base_height = int(orig_height * ratio)
        else:
            base_width, base_height = orig_width, orig_height

        total_scale = scale * self.zoom_level
        new_width = max(20, int(base_width * total_scale))
        new_height = max(20, int(base_height * total_scale))
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(img_resized)

        insert_pos = at_index if at_index else self.text_area.index(tk.INSERT)
        img_name = self.text_area.image_create(insert_pos, image=photo)
        self.global_images[img_name] = photo

        tag_name = f"img_{img_name}"
        self.text_area.tag_add(tag_name, insert_pos, f"{insert_pos}+1c")

        if at_index is None:
            self.text_area.mark_set(tk.INSERT, f"{insert_pos}+1c")

        self.text_area.tag_bind(tag_name, "<Double-Button-1>", lambda e, fn=filename: self.show_image_lightbox(fn))
        self.text_area.tag_bind(tag_name, "<Button-3>", lambda e, nm=img_name: self.show_image_context_menu(e, nm))

        self.image_info[img_name] = {
            "filename": filename,
            "scale": scale,
            "base_width": base_width,
            "base_height": base_height,
            "tag": tag_name
        }

    def on_paste(self, event):
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                filename = f"img_{int(time.time() * 1000)}.png"
                img_path = os.path.join(self.IMG_DIR, filename)
                img.save(img_path, "PNG")
                self.image_cache[filename] = img.convert("RGBA")
                self._insert_image(img_path, filename, scale=1.0)
                self.save_notes()
                return "break"
        except Exception:
            self.logger.exception("Panodan resim yapistirilamadi")

        if self._save_job:
            self.app.after_cancel(self._save_job)
        self._save_job = self.app.after(100, self.auto_save_and_highlight)

    def _selection_contains_image(self, sel_first, sel_last):
        for info in self.image_info.values():
            ranges = self.text_area.tag_ranges(info["tag"])
            if not ranges:
                continue
            r0, r1 = ranges[0], ranges[1]
            if self.text_area.compare(sel_first, "<=", r0) and self.text_area.compare(r1, "<=", sel_last):
                return True
        return False

    def on_cut(self, event=None):
        """Windows'un varsayilan Ctrl+X davranisi, secim bir gorsel
        iceriyorsa gorseli panoya kopyalamadan siler (Tk'nin get() komutu
        gomulu gorselleri metne dahil etmiyor) - yani 'kestim, sonra
        yapistiririm' diye dusunen kullanici gorseli geri getiremiyordu.
        Burada secimde gorsel varsa once onay istiyoruz; yoksa varsayilan
        kesme davranisina (kopyala + sil) hicbir mudahale etmeden izin
        veriyoruz."""
        try:
            if not self.text_area.tag_ranges(tk.SEL):
                return None  # secim yok, varsayilan davransin

            sel_first = self.text_area.index(tk.SEL_FIRST)
            sel_last = self.text_area.index(tk.SEL_LAST)

            if not self._selection_contains_image(sel_first, sel_last):
                return None  # gorsel yok, varsayilan kes islemi (kopyala+sil) calissin

            onay = messagebox.askyesno(
                "Görsel İçeren Seçim",
                "Seçiminiz bir görsel içeriyor. Görseller panoya kopyalanamıyor; "
                "onaylarsanız hem metin hem görsel kalıcı olarak silinecek ve "
                "daha sonra yapıştırarak geri getiremeyeceksiniz.\n\n"
                "Devam edilsin mi?",
                parent=self.app,
            )
            if onay:
                self.text_area.delete(sel_first, sel_last)
                self.on_key_release(None)
            return "break"  # varsayilan kesme islemi hicbir kosulda calismasin
        except Exception:
            self.logger.exception("Ctrl+X (kesme) isleminde hata")
            return "break"

    def show_image_context_menu(self, event, img_name):
        if img_name not in self.image_info:
            return "break"

        info = self.image_info[img_name]
        filename = info["filename"]

        menu = Menu(self.app, tearoff=0)
        menu.add_command(label="Büyüt (%25)", command=lambda: self.resize_image(img_name, 1.25))
        menu.add_command(label="Küçült (%25)", command=lambda: self.resize_image(img_name, 0.8))
        menu.add_command(label="Orijinal Boyut", command=lambda: self.resize_image(img_name, 1.0, reset=True))
        menu.add_separator()
        menu.add_command(label="Resmi Panoya Kopyala", command=lambda: self.copy_image_to_clipboard(filename))
        menu.add_command(label="Farklı Kaydet...", command=lambda: self.save_image_as(filename))
        menu.add_separator()
        menu.add_command(label="Görseli Sil", command=lambda: self.delete_image(img_name))

        menu.post(event.x_root, event.y_root)
        return "break"

    def resize_image(self, img_name, factor, reset=False):
        info = self.image_info.get(img_name)
        if not info:
            return

        tag_name = info["tag"]
        ranges = self.text_area.tag_ranges(tag_name)
        if not ranges:
            return

        filename = info["filename"]
        img = self.image_cache.get(filename)
        if not img:
            img_path = os.path.join(self.IMG_DIR, filename)
            if os.path.exists(img_path):
                try:
                    img = Image.open(img_path).convert("RGBA")
                    self.image_cache[filename] = img
                except Exception:
                    self.logger.exception(f"Yeniden boyutlandirmada gorsel acilamadi: {img_path}")
                    img = None

        if not img:
            return

        new_scale = 1.0 if reset else info["scale"] * factor
        total_scale = new_scale * self.zoom_level
        new_width = max(20, int(info["base_width"] * total_scale))
        new_height = max(20, int(info["base_height"] * total_scale))

        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img_resized)

        self.global_images[img_name] = photo
        self.text_area.image_configure(ranges[0], image=photo)
        self.image_info[img_name]["scale"] = new_scale
        self.save_notes()

    def show_image_lightbox(self, filename):
        img_path = os.path.join(self.IMG_DIR, filename)
        if not os.path.exists(img_path):
            return

        top = tk.Toplevel(self.app)
        top.overrideredirect(True)
        top.attributes("-topmost", True)
        top.configure(bg="#0F172A")

        img = Image.open(img_path)
        screen_w = top.winfo_screenwidth()
        screen_h = top.winfo_screenheight()

        max_w = int(screen_w * 0.85)
        max_h = int(screen_h * 0.85)

        w, h = img.size
        ratio = min(max_w / w, max_h / h, 1.0)
        new_w, new_h = max(100, int(w * ratio)), max(100, int(h * ratio))

        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(resized)

        x = (screen_w - new_w) // 2
        y = (screen_h - new_h) // 2
        top.geometry(f"{new_w}x{new_h}+{x}+{y}")

        lbl = tk.Label(top, image=photo, bg="#0F172A", bd=0, cursor="hand2")
        lbl.image = photo
        lbl.pack(expand=True, fill="both")

        top.bind("<Button-1>", lambda e: top.destroy())
        top.bind("<Escape>", lambda e: top.destroy())
        top.bind("<FocusOut>", lambda e: top.destroy())
        top.focus_force()

    def copy_image_to_clipboard(self, filename):
        img_path = os.path.join(self.IMG_DIR, filename)
        if not os.path.exists(img_path):
            return
        try:
            copy_image_to_windows_clipboard(img_path)
            self.show_temp_message("Resim Kopyalandı")
        except Exception:
            self.logger.exception(f"Gorsel panoya kopyalanamadi: {filename}")
            self.show_temp_message("Kopyalama başarısız")

    def save_image_as(self, filename):
        img_path = os.path.join(self.IMG_DIR, filename)
        if not os.path.exists(img_path):
            return
        dest = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Dosyaları", "*.png"), ("Tüm Dosyalar", "*.*")],
            initialfile=filename
        )
        if dest:
            shutil.copyfile(img_path, dest)
            self.show_temp_message("Dışa Aktarıldı")

    def delete_image(self, img_name):
        info = self.image_info.get(img_name)
        if not info:
            return
        tag_name = info["tag"]
        ranges = self.text_area.tag_ranges(tag_name)
        if ranges:
            self.text_area.delete(ranges[0], ranges[1])
        if img_name in self.image_info:
            del self.image_info[img_name]
        if img_name in self.global_images:
            del self.global_images[img_name]
        self.save_notes()
        self.show_temp_message("Görsel Silindi")

    def clean_unused_images(self):
        """Hicbir sayfada (aktif ya da arsivlenmis) referans verilmeyen
        gorselleri SILMEZ; images/_unused/ altina tasir. Once mevcut
        sayfa diskte guncel olsun diye kaydediliyor, aksi halde henuz
        otomatik kaydedilmemis en son degisiklikler tarama disinda
        kalabilirdi."""
        self.save_notes()
        referenced = find_referenced_images(self.DATA_DIR)
        try:
            moved = move_unused_images(self.IMG_DIR, referenced)
        except Exception:
            self.logger.exception("Kullanilmayan gorseller temizlenemedi")
            self.show_temp_message("Temizleme başarısız")
            return
        if moved:
            self.show_temp_message(f"{len(moved)} görsel '_unused' klasörüne taşındı")
        else:
            self.show_temp_message("Taşınacak görsel yok")
