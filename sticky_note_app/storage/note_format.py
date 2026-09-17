"""Sayfa dosyalarinin (.txt) metin+gorsel formatini ayristirma/olusturma.

Bu modul kasitli olarak Tkinter'a hic dokunmuyor - sadece duz metin ve
sozlukler uzerinde calisiyor. Boylece GUI acmadan (pytest ile) test
edilebiliyor. Orijinal tek-dosyalik uygulamada bu mantik load_notes() ve
save_notes() metodlarinin icine gomulmustu; davranis BIREBIR AYNI, sadece
Tkinter'dan ayristirildi.
"""
import re

IMAGE_TAG_PATTERN = re.compile(r"(\[RESIM:.*?\])")


def parse_segments(content):
    """Sayfa metnini sirali (tur, ...) parcalarina ayirir:
      ("text", metin)
      ("image", dosya_adi, olcek)
    Cagiran taraf (NotesMixin.load_notes) bu listeyi gezip metni/gorselleri
    text_area'ya ekler.
    """
    segments = []
    parts = IMAGE_TAG_PATTERN.split(content)
    for part in parts:
        if part.startswith("[RESIM:") and part.endswith("]"):
            img_tag = part[7:-1]
            if "|" in img_tag:
                filename, scale_str = img_tag.split("|", 1)
                try:
                    scale = float(scale_str)
                except ValueError:
                    scale = 1.0
            else:
                filename = img_tag
                scale = 1.0
            segments.append(("image", filename, scale))
        elif part:
            segments.append(("text", part))
    return segments


def serialize_dump(dump_items, image_info):
    """text_area.dump(...) ciktisini (key, value, index) uclulerinden
    olusan bir liste/iterable olarak alir ve image_info sozlugunu kullanarak
    diske yazilacak duz metni uretir. Orijinal save_notes() ile BIREBIR AYNI
    bicimi uretir: [RESIM:dosya|olcek] etiketleri.
    """
    content = ""
    for key, value, index in dump_items:
        if key == "text":
            content += value
        elif key == "image":
            info = image_info.get(value, {})
            filename = info.get("filename", "")
            scale = info.get("scale", 1.0)
            if filename:
                content += f"[RESIM:{filename}|{scale}]"
    return content
