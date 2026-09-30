# PixelsPDFJPG

Windows icin PDF ve gorsel donusturucu. Uygulama CustomTkinter arayuzuyle calisir; PDF islemlerinde PyMuPDF, gorsel islemlerinde Pillow kullanir.

## Ozellikler

- Bir veya daha fazla gorseli tek PDF'te birlestirme ya da ayri PDF'ler olusturma
- PDF sayfalarini JPG, PNG, BMP, GIF veya TIF olarak disa aktarma
- Sayfa boyutu, kenar bosluklari, renk modu ve DPI secenekleri

## Hazir uygulama

Windows icin paketlenmis surum: [`dist/PixelsPDFJPG.exe`](dist/PixelsPDFJPG.exe)

## Kaynaktan calistirma

Python 3.10 veya daha yenisini kurun. Proje klasorunde:

```powershell
py -m pip install -r requirements.txt
py main.py
```

## Windows EXE olusturma

```powershell
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --clean --onefile --windowed --name PixelsPDFJPG --collect-all customtkinter --collect-all pymupdf main.py
```

Paketlenmis dosya `dist/PixelsPDFJPG.exe` yolunda olusur. Windows EXE'sini Windows uzerinde olusturun.