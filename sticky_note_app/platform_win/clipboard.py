"""Windows'a ozgu pano (clipboard) islemleri.

ctypes.windll kullanan tum kod bilerek burada, tek bir dosyada izole
edildi (orijinalde copy_image_to_clipboard metodunun icindeydi).
"""
import io
import ctypes

from PIL import Image

GMEM_MOVEABLE = 0x0002
CF_DIB = 8


def copy_image_to_windows_clipboard(img_path):
    """Verilen gorsel dosyasini BMP'ye cevirip Windows panosuna DIB olarak
    yazar. Hata durumunda exception firlatir; cagiran taraf (ImageMixin)
    yakalayip loglar ve kullaniciya mesaj gosterir."""
    img = Image.open(img_path).convert("RGB")
    output = io.BytesIO()
    img.save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    h_cd = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
    p_cd = kernel32.GlobalLock(h_cd)
    ctypes.memmove(p_cd, data, len(data))
    kernel32.GlobalUnlock(h_cd)

    user32.OpenClipboard(None)
    user32.EmptyClipboard()
    user32.SetClipboardData(CF_DIB, h_cd)
    user32.CloseClipboard()
