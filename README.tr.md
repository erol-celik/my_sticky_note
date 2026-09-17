# My Sticky Note

Python ve Tkinter ile gelistirilmis, her zaman en ustte kalabilen, hafif bir Windows masaustu yapiskan not uygulamasi.

## Ozellikler

- Her biri kendi duz metin dosyasina kaydedilen birden fazla not ("sayfa")
- Uygulamayi her yerden gosterip gizlemek icin genel klavye kisayolu (`Alt+"`)
- Not icine dogrudan resim yapistirma ve yonetme
- Vurgulamali, ileri/geri gezinmeli not ici arama
- Otomatik kaydetme, periyodik yedekleme ve guvenli (atomic) dosya yazma
- Sayfa yeniden adlandirma/silme (silme islemi anlik degil, arsivleme seklinde)
- Pencere konumu, boyutu, son acik sayfa ve yakinlastirma (zoom) seviyesini hatirlama
- PyInstaller ile tek dosyalik bagimsiz `.exe` olarak paketlenebilir (calistirmak icin Python kurulumu gerekmez)

## Gereksinimler

- Python 3.12+ (yalnizca kaynak koddan calistirmak icin gerekli; paketlenmis `.exe` icin gerekmez)
- Windows (uygulama genel kisayol ve pano/resim destegi icin Windows'a ozgu API'ler kullanir)
- Kod tarafindan kullanilan ucuncu parti paketler:
  - [`Pillow`](https://pypi.org/project/Pillow/) (resim isleme)
  - [`keyboard`](https://pypi.org/project/keyboard/) (genel klavye kisayolu)
  - [`pyinstaller`](https://pypi.org/project/pyinstaller/) (yalnizca `.exe` derlemek icin)

> Not: bu depoda su an bir `requirements.txt` / `pyproject.toml` bulunmuyor. Bu dosya eklenene kadar yukaridaki paketleri elle kurun.

## Kurulum

```bash
git clone <bu-deponun-url'si>
cd my_sticky_note
pip install pillow keyboard pyinstaller
```

## Kullanim

Kaynak koddan calistirmak icin:

```bash
python my_sticky_note.py
```

Not penceresini gostermek/gizlemek icin istediginiz an `Alt+"` tusuna basin.

Notlar ve resimler, script'in (veya paketlendiginde `.exe`'nin) yaninda olusturulan `my_sticky_data/` klasoru altinda saklanir; boylece verileriniz her zaman uygulamayla birlikte tasinir.

### Bagimsiz calistirilabilir dosya (exe) olusturma

```bash
pyinstaller my_sticky_note.spec
```

Olusan calistirilabilir dosya `dist/my_sticky_note.exe` konumuna yazilir.

## Proje yapisi

```
my_sticky_note.py          Giris noktasi
my_sticky_note.spec        PyInstaller derleme dosyasi
sticky_note_app/
  app.py                   Ana uygulama sinifi
  config.py                Renk/gorunum sabitleri
  logging_setup.py         Donen (rotating) dosya loglama ayari
  platform_win/            Windows'a ozgu entegrasyonlar (pano)
  storage/                 Sayfa/ayar/yedek/resim kalicilik islemleri
  ui/                      Tkinter arayuz mixin'leri (pencere, sayfalar, metin editoru, resimler, arama, kisayollar)
```

## Lisans

Bu depoda su an bir lisans dosyasi bulunmuyor. Bir lisans eklenmedigi surece tum haklar yazara aittir.
