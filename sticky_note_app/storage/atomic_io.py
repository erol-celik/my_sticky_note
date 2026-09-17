"""Dosyaya guvenli (atomik) yazma.

Once gecici (.tmp) dosyaya yazilir, sonra isim degistirilerek (os.replace)
asil dosyanin yerine konur. Boylece yazma sirasinda uygulama cokerse ya da
kapatilirsa orijinal dosya yarim/bos kalmaz - ya eski hali ya da tam yeni
hali durur.
"""
import os


def atomic_write(path, content):
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)
