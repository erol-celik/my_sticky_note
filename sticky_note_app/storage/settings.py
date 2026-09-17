"""Kullanici ayarlarinin (pencere konumu/boyutu, son sayfa, zoom) kalici
olarak saklanmasi (Faz 4).

JSON dosyasi bozuksa, eksikse ya da hic yoksa guvenli varsayilanlara
donulur - uygulama ASLA bu yuzden acilmayi reddetmez ya da hata vermez.
"""
import json
import os

from .atomic_io import atomic_write

SETTINGS_FILENAME = "settings.json"

DEFAULT_SETTINGS = {
    "geometry": "560x420+150+120",
    "zoom_level": 1.0,
    "last_page": "Sayfa 1",
}


def settings_path(data_dir):
    return os.path.join(data_dir, SETTINGS_FILENAME)


def load_settings(data_dir):
    path = settings_path(data_dir)
    settings = dict(DEFAULT_SETTINGS)
    if not os.path.exists(path):
        return settings
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            for key in DEFAULT_SETTINGS:
                if key in data:
                    settings[key] = data[key]
    except Exception:
        pass  # bozuk/okunamayan dosya -> guvenli varsayilanlar kullanilir
    return settings


def save_settings(data_dir, settings):
    path = settings_path(data_dir)
    payload = {key: settings.get(key, DEFAULT_SETTINGS[key]) for key in DEFAULT_SETTINGS}
    atomic_write(path, json.dumps(payload, ensure_ascii=False, indent=2))
