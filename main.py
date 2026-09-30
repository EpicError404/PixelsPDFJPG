import sys
import os
import subprocess
import winsound

try:
    import customtkinter as ctk
    import pymupdf
    from PIL import Image
except ImportError:
    print("[VS Code] Gerekli kütüphaneler kuruluyor...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "customtkinter", "pymupdf", "Pillow"
    ])
    os.execv(sys.executable, [sys.executable] + sys.argv)

import threading
from converter_engine import ConverterEngine
from ui_views import AndroidHomeScreen, ImageToPdfApp, PdfToImageApp


def play_completion_sound():
    sound_candidates = [
        r"C:\Windows\Media\Windows Notify System Generic.wav",
        r"C:\Windows\Media\Windows Notify.wav",
        r"C:\Windows\Media\notify.wav",
        r"C:\Windows\Media\chimes.wav",
        r"C:\Windows\Media\tada.wav"
    ]
    for sound_path in sound_candidates:
        if os.path.exists(sound_path):
            winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return
    winsound.MessageBeep(winsound.MB_ICONASTERISK)


def open_folder_in_explorer(folder_path: str):
    """Windows 11 Dosya Gezgini'nde belirtilen klasörü açar."""
    try:
        norm_path = os.path.normpath(os.path.abspath(folder_path))
        if os.path.exists(norm_path):
            os.startfile(norm_path)
    except Exception as ex:
        print(f"Klasör açılamadı: {ex}")


class AndroidVirtualDevice(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PixelsPDFJPG")
        self.geometry("420x890")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")

        # Android Telefon Kasası
        self.phone_chassis = ctk.CTkFrame(
            self, corner_radius=36, fg_color="#0D1017",
            border_width=4, border_color="#2A2F3D"
        )
        self.phone_chassis.pack(fill="both", expand=True, padx=8, pady=8)

        # İlerleme Çubuğu
        self.progress_bar = ctk.CTkProgressBar(self.phone_chassis, height=3, fg_color="#1E232E", progress_color="#00E5FF")
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=14, pady=(12, 2))
        self.progress_bar.pack_forget()

        # Ekran Alanı
        self.screen_container = ctk.CTkFrame(self.phone_chassis, fg_color="transparent")
        self.screen_container.pack(fill="both", expand=True, padx=12, pady=(10, 6))

        # Android 3 Tuşlu Gezinme Çubuğu (◀  ●  ■)
        self.nav_bar = ctk.CTkFrame(self.phone_chassis, height=44, corner_radius=18, fg_color="#131720")
        self.nav_bar.pack(fill="x", padx=14, pady=(2, 10))

        ctk.CTkButton(
            self.nav_bar, text="◀", font=("Segoe UI", 15), width=70, height=32,
            fg_color="transparent", hover_color="#232938", text_color="#B0B8C4",
            command=lambda: self.switch_screen("home")
        ).pack(side="left", expand=True)

        ctk.CTkButton(
            self.nav_bar, text="●", font=("Segoe UI", 16), width=70, height=32,
            fg_color="transparent", hover_color="#232938", text_color="#B0B8C4",
            command=lambda: self.switch_screen("home")
        ).pack(side="left", expand=True)

        ctk.CTkButton(
            self.nav_bar, text="■", font=("Segoe UI", 15), width=70, height=32,
            fg_color="transparent", hover_color="#232938", text_color="#B0B8C4",
            command=lambda: self.show_toast("Tüm pencereler arka planda hazır")
        ).pack(side="left", expand=True)

        self.home_screen = AndroidHomeScreen(self.screen_container, self.switch_screen)
        self.img_app = ImageToPdfApp(self.screen_container, self.start_img2pdf)
        self.pdf_app = PdfToImageApp(self.screen_container, self.start_pdf2img)

        self.current_screen = None
        self.switch_screen("home")

    def switch_screen(self, screen_name):
        if self.current_screen:
            self.current_screen.pack_forget()

        if screen_name == "home":
            self.current_screen = self.home_screen
        elif screen_name == "img2pdf":
            self.current_screen = self.img_app
        elif screen_name == "pdf2img":
            self.current_screen = self.pdf_app

        self.current_screen.pack(fill="both", expand=True)

    def show_toast(self, text):
        toast = ctk.CTkLabel(
            self.phone_chassis, text=text, fg_color="#262D3D",
            text_color="#FFFFFF", corner_radius=16, height=32, font=("Segoe UI", 11)
        )
        toast.place(relx=0.5, rely=0.88, anchor="center")
        self.after(2600, toast.destroy)

    def start_img2pdf(self, opts):
        if not opts["images"]:
            self.show_toast("Lütfen görsel ekleyin!")
            return

        def task():
            self.progress_bar.pack(fill="x", padx=14, pady=(12, 2))
            self.progress_bar.set(0.2)
            try:
                def prog(cur, tot):
                    self.progress_bar.set(cur / tot)

                out = ConverterEngine.convert_images_to_pdf(opts["images"], opts, prog)
                self.progress_bar.pack_forget()
                play_completion_sound()
                self.show_toast(f"Tamamlandı: {len(out)} PDF kaydedildi.")

                # Windows 11: Dosyanın kaydedildiği klasörü Dosya Gezgini'nde aç
                if out:
                    save_dir = os.path.dirname(os.path.abspath(out[0]))
                    open_folder_in_explorer(save_dir)
            except Exception as e:
                self.progress_bar.pack_forget()
                self.show_toast(f"Hata: {str(e)}")

        threading.Thread(target=task, daemon=True).start()

    def start_pdf2img(self, opts):
        if not opts["pdf_paths"]:
            self.show_toast("Lütfen PDF dosyası ekleyin!")
            return

        def task():
            self.progress_bar.pack(fill="x", padx=14, pady=(12, 2))
            self.progress_bar.set(0.2)
            try:
                def prog(cur, tot):
                    self.progress_bar.set(cur / tot)

                out = ConverterEngine.convert_pdf_to_images(
                    opts["pdf_paths"], opts["output_folder"],
                    fmt=opts["format"], dpi=opts["dpi"], progress_cb=prog
                )
                self.progress_bar.pack_forget()
                play_completion_sound()
                self.show_toast(f"Tamamlandı: {len(out)} görsel kaydedildi.")

                # Windows 11: Görsellerin kaydedildiği klasörü Dosya Gezgini'nde aç
                if out:
                    save_dir = os.path.dirname(os.path.abspath(out[0]))
                    open_folder_in_explorer(save_dir)
            except Exception as e:
                self.progress_bar.pack_forget()
                self.show_toast(f"Hata: {str(e)}")

        threading.Thread(target=task, daemon=True).start()


if __name__ == "__main__":
    app = AndroidVirtualDevice()
    app.mainloop()