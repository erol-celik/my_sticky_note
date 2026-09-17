"""Sayfa ici arama (Ctrl+F) - Faz 3'te eklenen yeni ozellik.

Ctrl+F ile metin alaninin ustunde kucuk bir arama cubugu acilir; yazarken
tum eslesmeler vurgulanir, Enter/Shift+Enter ile sonraki/onceki eslesmeye
gidilir, Escape ile kapanir. Salt-okunur bir arama - hicbir metni degistirmez.

Arama cubugu ilk Ctrl+F'e kadar hic olusturulmaz (tembel/lazy kurulum),
boylece baslangic performansini etkilemez.
"""
import tkinter as tk


class SearchMixin:
    def setup_search_bar(self):
        self.search_frame = None
        self._search_matches = []
        self._search_current_idx = -1
        self.text_area.bind("<Control-f>", self.open_search_bar)
        self.text_area.bind("<Control-F>", self.open_search_bar)

    def _ensure_search_bar(self):
        if self.search_frame is not None:
            return

        self.text_area.tag_config("search_match", background="#FDE68A")
        self.text_area.tag_config("search_current", background="#F59E0B")

        self.search_frame = tk.Frame(self.app, bg=self.RENK_UST)

        self.search_entry = tk.Entry(self.search_frame, font=("Segoe UI", 10))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(8, 4), pady=4)
        self.search_entry.bind("<KeyRelease>", self._on_search_key_release)
        self.search_entry.bind("<Return>", lambda e: self.search_next())
        self.search_entry.bind("<Shift-Return>", lambda e: self.search_prev())
        self.search_entry.bind("<Escape>", self.close_search_bar)

        self.search_count_label = tk.Label(
            self.search_frame, text="", bg=self.RENK_UST, fg="#93C5FD", font=("Segoe UI", 9)
        )
        self.search_count_label.pack(side="left", padx=4)

        search_close_btn = tk.Label(
            self.search_frame, text="✕", bg=self.RENK_UST, fg="#FFFFFF",
            font=("Segoe UI", 10, "bold"), cursor="hand2", padx=8
        )
        search_close_btn.pack(side="right")
        search_close_btn.bind("<Button-1>", self.close_search_bar)

    def open_search_bar(self, event=None):
        self._ensure_search_bar()
        if not self.search_frame.winfo_ismapped():
            # Metin alanini gecici olarak sokup arama cubugunu ustune,
            # sonra metin alanini AYNI parametrelerle tekrar paketliyoruz -
            # boylece arama cubugu metin alaninin USTUNDE gorunuyor.
            self.text_area.pack_forget()
            self.search_frame.pack(fill="x", side="top")
            self.text_area.pack(expand=True, fill="both", padx=12, pady=(10, 16))
        self.search_entry.focus_set()
        self.search_entry.select_range(0, "end")
        return "break"

    def close_search_bar(self, event=None):
        if self.search_frame is not None and self.search_frame.winfo_ismapped():
            self.search_frame.pack_forget()
        self.text_area.tag_remove("search_match", "1.0", "end")
        self.text_area.tag_remove("search_current", "1.0", "end")
        self._search_matches = []
        self._search_current_idx = -1
        self.text_area.focus_set()
        return "break"

    def _on_search_key_release(self, event=None):
        if event is not None and event.keysym in ("Return", "Escape", "Shift_L", "Shift_R"):
            return  # bunlar kendi binding'leriyle yonetiliyor
        self._recompute_search(self.search_entry.get())

    def _recompute_search(self, query):
        self._search_matches = self._find_all_matches(query)
        self._search_current_idx = 0 if self._search_matches else -1
        self._update_search_highlights()
        self._update_search_count_label()

    def _find_all_matches(self, query):
        matches = []
        if not query:
            return matches
        start = "1.0"
        while True:
            pos = self.text_area.search(query, start, stopindex="end", nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(query)}c"
            matches.append((pos, end))
            start = end
        return matches

    def _update_search_highlights(self):
        self.text_area.tag_remove("search_match", "1.0", "end")
        self.text_area.tag_remove("search_current", "1.0", "end")
        for start, end in self._search_matches:
            self.text_area.tag_add("search_match", start, end)
        if self._search_matches and 0 <= self._search_current_idx < len(self._search_matches):
            cur_start, cur_end = self._search_matches[self._search_current_idx]
            self.text_area.tag_add("search_current", cur_start, cur_end)
            self.text_area.tag_raise("search_current")
            self.text_area.see(cur_start)

    def _update_search_count_label(self):
        if not self._search_matches:
            text = "0/0" if self.search_entry.get() else ""
        else:
            text = f"{self._search_current_idx + 1}/{len(self._search_matches)}"
        self.search_count_label.config(text=text)

    def search_next(self, event=None):
        if not self._search_matches:
            return "break"
        self._search_current_idx = (self._search_current_idx + 1) % len(self._search_matches)
        self._update_search_highlights()
        self._update_search_count_label()
        return "break"

    def search_prev(self, event=None):
        if not self._search_matches:
            return "break"
        self._search_current_idx = (self._search_current_idx - 1) % len(self._search_matches)
        self._update_search_highlights()
        self._update_search_count_label()
        return "break"
