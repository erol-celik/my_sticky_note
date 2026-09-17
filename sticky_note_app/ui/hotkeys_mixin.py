"""Genel (global) klavye kisayolu ve gorunurluk acma/kapama.

Orijinal setup_hotkeys() / toggle_visibility() ile BIREBIR AYNI; alt+"
kisayolu KASITLI OLARAK degistirilmedi.
"""
import keyboard


class HotkeysMixin:
    def setup_hotkeys(self):
        # NOT: kisayol kasitli olarak degistirilmedi (alt+"), sadece kayit
        # basarisiz olursa artik sessizce degil, log dosyasina yazarak yutuluyor.
        try:
            keyboard.add_hotkey('alt+"', lambda: self.app.after(0, self.toggle_visibility))
        except Exception:
            self.logger.exception("Genel kisayol (alt+\") kaydedilemedi")

    def toggle_visibility(self):
        if self.is_visible:
            self.app.withdraw()
        else:
            self.app.deiconify()
            self.app.overrideredirect(True)
            self.app.attributes("-topmost", True)
            self.app.lift()
            self.text_area.focus_force()
        self.is_visible = not self.is_visible
