"""Metin alani: kurulum, tum Ctrl/Tab kisayollari, yakinlastirma, baglanti
vurgulama. Orijinal dosyadaki ilgili metodlarin BIREBIR AYNI tasinmis hali
(Faz 1'de eklenen Ctrl+Shift+Z duzeltmesi, Ctrl+X gorsel korumasi ve
Shift+Tab/coklu satir girinti burada, degismeden duruyor).
"""
import os
import re
import webbrowser
import tkinter as tk

from PIL import Image, ImageTk


class TextEditorMixin:
    def setup_text_area(self):
        self.text_area = tk.Text(
            self.app,
            bg=self.RENK_ALT,
            fg=self.YAZI_RENGI,
            font=("Segoe UI", self.base_font_size),
            relief="flat",
            wrap="word",
            insertbackground=self.YAZI_RENGI,
            undo=True,
            maxundo=100,
            autoseparators=True
        )
        self.text_area.pack(expand=True, fill="both", padx=12, pady=(10, 16))

        # Baglanti Ayarlari
        self.text_area.tag_config("hyperlink", foreground="#2563EB", underline=1)
        self.text_area.tag_bind("hyperlink", "<Control-Button-1>", self.open_link)
        self.text_area.tag_bind("hyperlink", "<Enter>", lambda e: self.text_area.config(cursor="hand2"))
        self.text_area.tag_bind("hyperlink", "<Leave>", lambda e: self.text_area.config(cursor="xterm"))

        self.setup_text_bindings()

    def setup_text_bindings(self):
        self.text_area.bind("<Control-BackSpace>", self.on_ctrl_backspace)
        self.text_area.bind("<Control-Delete>", self.on_ctrl_delete)
        self.text_area.bind("<Control-a>", self.select_all)
        self.text_area.bind("<Control-A>", self.select_all)
        self.text_area.bind("<Control-z>", self.on_ctrl_z)
        self.text_area.bind("<Control-Z>", self.on_ctrl_z)
        self.text_area.bind("<Control-y>", self.redo)
        self.text_area.bind("<Control-Y>", self.redo)
        self.text_area.bind("<Control-d>", self.duplicate_line)
        self.text_area.bind("<Control-D>", self.duplicate_line)
        self.text_area.bind("<Control-Shift-K>", self.delete_line)
        self.text_area.bind("<Control-Shift-k>", self.delete_line)
        self.text_area.bind("<Tab>", self.handle_tab)
        self.text_area.bind("<Shift-Tab>", self.handle_shift_tab)

        self.text_area.bind("<<Paste>>", self.on_paste)
        self.text_area.bind("<<Cut>>", self.on_cut)
        self.text_area.bind("<KeyRelease>", self.on_key_release)
        self.text_area.bind("<MouseWheel>", self.on_mouse_wheel)
        self.app.bind_all("<Control-s>", lambda e: self.save_notes_with_message())
        self.app.bind_all("<Control-plus>", lambda e: self.zoom_step(1.1))
        self.app.bind_all("<Control-equal>", lambda e: self.zoom_step(1.1))
        self.app.bind_all("<Control-minus>", lambda e: self.zoom_step(0.9))
        self.app.bind_all("<Control-0>", lambda e: self.apply_zoom(1.0))

    def highlight_links(self):
        self.text_area.tag_remove("hyperlink", "1.0", "end")
        text = self.text_area.get("1.0", "end")
        url_pattern = r'(https?://[^\s<>"]+|www\.[^\s<>"]+)'

        for match in re.finditer(url_pattern, text):
            start_idx = f"1.0 + {match.start()} chars"
            end_idx = f"1.0 + {match.end()} chars"
            self.text_area.tag_add("hyperlink", start_idx, end_idx)

    def open_link(self, event):
        click_index = self.text_area.index(f"@{event.x},{event.y}")
        ranges = self.text_area.tag_ranges("hyperlink")
        for i in range(0, len(ranges), 2):
            if self.text_area.compare(ranges[i], "<=", click_index) and self.text_area.compare(click_index, "<=", ranges[i+1]):
                url = self.text_area.get(ranges[i], ranges[i+1]).strip()
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                webbrowser.open(url)
                break
        return "break"

    def on_key_release(self, event):
        if self._save_job:
            self.app.after_cancel(self._save_job)
        self._save_job = self.app.after(400, self.auto_save_and_highlight)

    def on_ctrl_backspace(self, event):
        try:
            if self.text_area.tag_ranges(tk.SEL):
                self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            else:
                insert_pos = self.text_area.index(tk.INSERT)
                line_start = self.text_area.index(f"{insert_pos} linestart")
                text_before = self.text_area.get(line_start, insert_pos)

                if not text_before:
                    if self.text_area.compare(insert_pos, ">", "1.0"):
                        self.text_area.delete(f"{insert_pos}-1c", insert_pos)
                else:
                    match = re.search(r'(?:\w+|[^\w\s]+)\s*$', text_before)
                    if match:
                        del_len = len(match.group(0))
                        self.text_area.delete(f"{insert_pos}-{del_len}c", insert_pos)
                    else:
                        match_spaces = re.search(r'\s+$', text_before)
                        if match_spaces:
                            del_len = len(match_spaces.group(0))
                            self.text_area.delete(f"{insert_pos}-{del_len}c", insert_pos)
                        else:
                            self.text_area.delete(f"{insert_pos}-1c", insert_pos)
            self.on_key_release(None)
        except Exception:
            self.logger.exception("Ctrl+Backspace isleminde hata")
        return "break"

    def on_ctrl_delete(self, event):
        try:
            if self.text_area.tag_ranges(tk.SEL):
                self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            else:
                insert_pos = self.text_area.index(tk.INSERT)
                line_end = self.text_area.index(f"{insert_pos} lineend")
                text_after = self.text_area.get(insert_pos, line_end)

                if not text_after:
                    if self.text_area.compare(insert_pos, "<", "end-1c"):
                        self.text_area.delete(insert_pos, f"{insert_pos}+1c")
                else:
                    match = re.match(r'^\s*(?:\w+|[^\w\s]+)', text_after)
                    if match:
                        del_len = len(match.group(0))
                        self.text_area.delete(insert_pos, f"{insert_pos}+{del_len}c")
                    else:
                        self.text_area.delete(insert_pos, f"{insert_pos}+1c")
            self.on_key_release(None)
        except Exception:
            self.logger.exception("Ctrl+Delete isleminde hata")
        return "break"

    def select_all(self, event=None):
        self.text_area.tag_add(tk.SEL, "1.0", "end-1c")
        self.text_area.mark_set(tk.INSERT, "end-1c")
        self.text_area.see(tk.INSERT)
        return "break"

    def undo(self, event=None):
        try:
            self.text_area.edit_undo()
            self.on_key_release(None)
        except tk.TclError:
            pass  # geri alinacak bir sey yok, bu normal/beklenen bir durum
        return "break"

    def redo(self, event=None):
        try:
            self.text_area.edit_redo()
            self.on_key_release(None)
        except tk.TclError:
            pass  # ileri alinacak bir sey yok, bu normal/beklenen bir durum
        return "break"

    def on_ctrl_z(self, event=None):
        """Ctrl+z hem 'undo' hem (Caps Lock acikken) 'Z' olarak gelebiliyordu ve
        eskiden Ctrl+Shift+Z ile ayni zamanda cakisan iki ayri binding vardi
        (biri undo'ya biri redo'ya baglanmisti). Artik tek bir yerden, Shift
        tusunun gercekten basili olup olmadigina (event.state) bakarak karar
        veriyoruz: Shift basiliysa redo, degilse (Caps Lock dahil) undo."""
        shift_pressed = bool(event is not None and (event.state & 0x0001))
        if shift_pressed:
            return self.redo(event)
        return self.undo(event)

    def duplicate_line(self, event=None):
        try:
            if self.text_area.tag_ranges(tk.SEL):
                sel_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.text_area.insert(tk.SEL_LAST, sel_text)
            else:
                insert_pos = self.text_area.index(tk.INSERT)
                line_start = self.text_area.index(f"{insert_pos} linestart")
                line_end = self.text_area.index(f"{insert_pos} lineend")
                line_text = self.text_area.get(line_start, line_end)
                self.text_area.insert(line_end, "\n" + line_text)
            self.on_key_release(None)
        except Exception:
            self.logger.exception("Satir kopyalama (Ctrl+D) isleminde hata")
        return "break"

    def delete_line(self, event=None):
        try:
            insert_pos = self.text_area.index(tk.INSERT)
            line_start = self.text_area.index(f"{insert_pos} linestart")
            line_next = self.text_area.index(f"{insert_pos}+1line linestart")
            if self.text_area.compare(line_next, "==", "end"):
                self.text_area.delete(line_start, "end-1c")
            else:
                self.text_area.delete(line_start, line_next)
            self.on_key_release(None)
        except Exception:
            self.logger.exception("Satir silme (Ctrl+Shift+K) isleminde hata")
        return "break"

    def handle_tab(self, event=None):
        try:
            if self.text_area.tag_ranges(tk.SEL):
                sel_first = self.text_area.index(tk.SEL_FIRST)
                sel_last = self.text_area.index(tk.SEL_LAST)
                first_line = int(sel_first.split(".")[0])
                last_line = int(sel_last.split(".")[0])
                last_col = int(sel_last.split(".")[1])
                if last_col == 0 and last_line > first_line:
                    last_line -= 1
                if last_line > first_line:
                    # Coklu satir secili: her satiri girintile (eski tek-satir
                    # davranisi asagida, degismeden korunuyor)
                    self._indent_lines(first_line, last_line, indent=True)
                    self.on_key_release(None)
                    return "break"
            self.text_area.insert(tk.INSERT, "    ")
            self.on_key_release(None)
        except Exception:
            self.logger.exception("Tab isleminde hata")
        return "break"

    def handle_shift_tab(self, event=None):
        try:
            if self.text_area.tag_ranges(tk.SEL):
                sel_first = self.text_area.index(tk.SEL_FIRST)
                sel_last = self.text_area.index(tk.SEL_LAST)
                first_line = int(sel_first.split(".")[0])
                last_line = int(sel_last.split(".")[0])
                last_col = int(sel_last.split(".")[1])
                if last_col == 0 and last_line > first_line:
                    last_line -= 1
            else:
                insert_pos = self.text_area.index(tk.INSERT)
                first_line = last_line = int(insert_pos.split(".")[0])
            self._indent_lines(first_line, last_line, indent=False)
            self.on_key_release(None)
        except Exception:
            self.logger.exception("Shift+Tab isleminde hata")
        return "break"

    def _indent_lines(self, first_line, last_line, indent=True):
        """Belirtilen satir araligini toplu girintiler (indent) ya da
        girintisini azaltir (dedent). Sadece Tab/Shift+Tab coklu satir
        secimlerinde kullanilir; tek satirlik eski Tab davranisina dokunmaz."""
        for line_no in range(first_line, last_line + 1):
            line_start = f"{line_no}.0"
            if indent:
                self.text_area.insert(line_start, "    ")
            else:
                line_text = self.text_area.get(line_start, f"{line_no}.end")
                if line_text.startswith("    "):
                    self.text_area.delete(line_start, f"{line_no}.4")
                elif line_text.startswith("\t"):
                    self.text_area.delete(line_start, f"{line_no}.1")
                else:
                    leading = len(line_text) - len(line_text.lstrip(" "))
                    if leading:
                        self.text_area.delete(line_start, f"{line_no}.{leading}")

    def zoom_step(self, factor):
        new_zoom = max(0.5, min(self.zoom_level * factor, 3.0))
        self.apply_zoom(new_zoom)

    def on_mouse_wheel(self, event):
        if event.state & 0x4:
            if event.delta > 0:
                self.zoom_step(1.1)
            else:
                self.zoom_step(0.9)
            return "break"

    def apply_zoom(self, new_zoom):
        self.zoom_level = new_zoom
        new_font_size = max(8, int(self.base_font_size * self.zoom_level))
        self.text_area.config(font=("Segoe UI", new_font_size))

        for img_name, info in list(self.image_info.items()):
            tag_name = info["tag"]
            ranges = self.text_area.tag_ranges(tag_name)
            if not ranges:
                continue

            filename = info["filename"]
            img = self.image_cache.get(filename)
            if not img:
                img_path = os.path.join(self.IMG_DIR, filename)
                if os.path.exists(img_path):
                    try:
                        img = Image.open(img_path).convert("RGBA")
                        self.image_cache[filename] = img
                    except Exception:
                        self.logger.exception(f"Zoom sirasinda gorsel acilamadi: {img_path}")
                        img = None

            if img:
                total_scale = info["scale"] * self.zoom_level
                new_width = max(20, int(info["base_width"] * total_scale))
                new_height = max(20, int(info["base_height"] * total_scale))

                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img_resized)

                self.global_images[img_name] = photo
                # Tkinter icin index olarak etiket baslangici verilir
                self.text_area.image_configure(ranges[0], image=photo)
