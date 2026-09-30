import os
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self._bind_widget(self.widget)

    def _bind_widget(self, w):
        w.bind("<Enter>", self.show_tip, add="+")
        w.bind("<Leave>", self.hide_tip, add="+")
        if hasattr(w, "_entry"):
            w._entry.bind("<Enter>", self.show_tip, add="+")
            w._entry.bind("<Leave>", self.hide_tip, add="+")

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        
        label = tk.Label(
            tw, text=self.text, justify=tk.LEFT,
            background="#252A36", foreground="#00E5FF",
            relief=tk.SOLID, borderwidth=1,
            font=("Segoe UI", 9, "bold"), padx=8, pady=4
        )
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class AndroidHomeScreen(ctk.CTkFrame):
    def __init__(self, master, open_app_cb):
        super().__init__(master, fg_color="transparent")
        self.open_app_cb = open_app_cb

        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(pady=(70, 25))
        ctk.CTkLabel(brand_frame, text="⚡", font=("Segoe UI Emoji", 46)).pack()
        ctk.CTkLabel(brand_frame, text="PixelsPDFJPG", font=("Segoe UI", 22, "bold"), text_color="#FFFFFF").pack(pady=(6, 0))
        ctk.CTkLabel(brand_frame, text="PDF & Resim Dönüştürücü", font=("Segoe UI", 13), text_color="#9AA0A6").pack()

        icons_row = ctk.CTkFrame(self, fg_color="transparent")
        icons_row.pack(pady=40)

        app1 = ctk.CTkButton(
            icons_row, text="📄\nResim > PDF", font=("Segoe UI", 13, "bold"),
            width=115, height=105, corner_radius=22, fg_color="#C62828", hover_color="#B71C1C",
            command=lambda: self.open_app_cb("img2pdf")
        )
        app1.pack(side="left", padx=14)

        app2 = ctk.CTkButton(
            icons_row, text="🖼\nPDF > Resim", font=("Segoe UI", 13, "bold"),
            width=115, height=105, corner_radius=22, fg_color="#1565C0", hover_color="#0D47A1",
            command=lambda: self.open_app_cb("pdf2img")
        )
        app2.pack(side="left", padx=14)


class ImageToPdfApp(ctk.CTkFrame):
    def __init__(self, master, on_start_convert):
        super().__init__(master, fg_color="transparent")
        self.on_start_convert = on_start_convert
        self.images = []

        bar = ctk.CTkFrame(self, height=40, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(bar, text="Resimden PDF'e", font=("Segoe UI", 16, "bold"), text_color="#FFFFFF").pack(side="left", padx=4)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="#181B22", corner_radius=16)
        self.scroll.pack(fill="both", expand=True, padx=2, pady=2)

        ctk.CTkLabel(self.scroll, text="Görsel Listesi", font=("Segoe UI", 12, "bold"), text_color="#90CAF9").pack(anchor="w", pady=(4, 2))
        self.list_box = ctk.CTkTextbox(self.scroll, height=85, corner_radius=8, font=("Consolas", 10))
        self.list_box.pack(fill="x", pady=4)

        btn_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_row.pack(fill="x", pady=2)
        ctk.CTkButton(btn_row, text="+ Görsel Ekle", width=90, height=28, fg_color="#2E7D32", hover_color="#1B5E20", command=self.pick_files).pack(side="left", padx=2)
        ctk.CTkButton(btn_row, text="Temizle", width=65, height=28, fg_color="#D32F2F", hover_color="#B71C1C", command=self.clear_files).pack(side="left", padx=2)

        ctk.CTkLabel(self.scroll, text="Ölçü & Sayfa Boyutu", font=("Segoe UI", 12, "bold"), text_color="#90CAF9").pack(anchor="w", pady=(10, 2))
        self.unit_seg = ctk.CTkSegmentedButton(self.scroll, values=["inches", "cm", "mm"])
        self.unit_seg.set("inches")
        self.unit_seg.pack(fill="x", pady=2)

        self.size_mode = ctk.CTkOptionMenu(
            self.scroll,
            values=["Görsel Boyutuna Eşitle (Match)", "Özel Boyut Belirle"]
        )
        self.size_mode.set("Görsel Boyutuna Eşitle (Match)")
        self.size_mode.pack(fill="x", pady=4)

        size_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        size_row.pack(fill="x", pady=2)
        self.w_entry = ctk.CTkEntry(size_row, placeholder_text="Genişlik", height=28); self.w_entry.insert(0, "8.5"); self.w_entry.pack(side="left", fill="x", expand=True, padx=2)
        self.h_entry = ctk.CTkEntry(size_row, placeholder_text="Yükseklik", height=28); self.h_entry.insert(0, "11.0"); self.h_entry.pack(side="left", fill="x", expand=True, padx=2)

        self.shrink_cb = ctk.CTkCheckBox(self.scroll, text="Büyük Görselleri Sayfaya Sığdır", font=("Segoe UI", 11)); self.shrink_cb.select(); self.shrink_cb.pack(anchor="w", pady=3)
        self.enlarge_cb = ctk.CTkCheckBox(self.scroll, text="Küçük Görselleri Sayfaya Büyüt", font=("Segoe UI", 11)); self.enlarge_cb.pack(anchor="w", pady=3)

        ctk.CTkLabel(self.scroll, text="Kenar Boşlukları (Margins)", font=("Segoe UI", 12, "bold"), text_color="#90CAF9").pack(anchor="w", pady=(8, 2))
        m_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        m_row.pack(fill="x", pady=2)
        self.m_top = ctk.CTkEntry(m_row, placeholder_text="Üst", width=50, height=26); self.m_top.insert(0, "0"); self.m_top.pack(side="left", padx=2)
        self.m_left = ctk.CTkEntry(m_row, placeholder_text="Sol", width=50, height=26); self.m_left.insert(0, "0"); self.m_left.pack(side="left", padx=2)
        self.m_bottom = ctk.CTkEntry(m_row, placeholder_text="Alt", width=50, height=26); self.m_bottom.insert(0, "0"); self.m_bottom.pack(side="left", padx=2)
        self.m_right = ctk.CTkEntry(m_row, placeholder_text="Sağ", width=50, height=26); self.m_right.insert(0, "0"); self.m_right.pack(side="left", padx=2)

        ctk.CTkLabel(self.scroll, text="Konum, Renk & DPI", font=("Segoe UI", 12, "bold"), text_color="#90CAF9").pack(anchor="w", pady=(8, 2))
        self.pos_seg = ctk.CTkSegmentedButton(self.scroll, values=["Ortala (Centered)", "Sol-Üst (Top-Left)"])
        self.pos_seg.set("Ortala (Centered)")
        self.pos_seg.pack(fill="x", pady=2)

        self.exif_cb = ctk.CTkCheckBox(self.scroll, text="EXIF Döndürmesini Kullan", font=("Segoe UI", 11)); self.exif_cb.select(); self.exif_cb.pack(anchor="w", pady=4)

        opt_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        opt_row.pack(fill="x", pady=2)
        self.color_mode = ctk.CTkOptionMenu(opt_row, values=["Orijinal", "CMYK", "Siyah-Beyaz"], width=140)
        self.color_mode.pack(side="left", padx=2)

        self.dpi_limit = ctk.CTkEntry(opt_row, placeholder_text="DPI", height=28)
        self.dpi_limit.insert(0, "150")
        self.dpi_limit.pack(side="left", fill="x", expand=True, padx=2)
        ToolTip(self.dpi_limit, "DPI Boyut Ayarı")

        ctk.CTkLabel(self.scroll, text="Çıktı Seçenekleri", font=("Segoe UI", 12, "bold"), text_color="#90CAF9").pack(anchor="w", pady=(8, 2))
        self.out_type = ctk.CTkSegmentedButton(self.scroll, values=["Tek PDF Birleştir", "Her Biri Ayrı PDF"])
        self.out_type.set("Tek PDF Birleştir")
        self.out_type.pack(fill="x", pady=2)

        self.pdf_name = ctk.CTkEntry(self.scroll, placeholder_text="PDF Adı", height=28); self.pdf_name.insert(0, "Belgelerim.pdf"); self.pdf_name.pack(fill="x", pady=3)

        out_f_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        out_f_row.pack(fill="x", pady=2)
        self.out_folder = ctk.CTkEntry(out_f_row, placeholder_text="Kayıt Klasörü (Varsayılan: Görsel Dizini)", height=28)
        self.out_folder.pack(side="left", fill="x", expand=True, padx=2)
        ctk.CTkButton(out_f_row, text="📁", width=34, height=28, command=self.pick_out_folder).pack(side="left", padx=2)

        ctk.CTkButton(
            self.scroll, text="PDF OLUŞTUR VE KAYDET", font=("Segoe UI", 13, "bold"),
            fg_color="#C62828", hover_color="#B71C1C", height=42, corner_radius=12,
            command=self.dispatch_convert
        ).pack(fill="x", pady=(14, 10))

    def pick_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("Görseller", "*.jpg *.jpeg *.png *.bmp *.gif *.tif *.webp")])
        if paths:
            for p in paths:
                if p not in self.images:
                    self.images.append(p)
            self.refresh_list()

    def clear_files(self):
        self.images.clear()
        self.refresh_list()

    def refresh_list(self):
        self.list_box.delete("1.0", "end")
        for p in self.images:
            self.list_box.insert("end", os.path.basename(p) + "\n")

    def pick_out_folder(self):
        f = filedialog.askdirectory()
        if f:
            self.out_folder.delete(0, "end")
            self.out_folder.insert(0, f)

    def dispatch_convert(self):
        try:
            dpi_val = int(float(self.dpi_limit.get().strip()))
        except Exception:
            dpi_val = 150

        opts = {
            "images": self.images,
            "unit": self.unit_seg.get(),
            "page_size_mode": self.size_mode.get(),
            "spec_width": float(self.w_entry.get() or 8.5),
            "spec_height": float(self.h_entry.get() or 11.0),
            "shrink_oversized": bool(self.shrink_cb.get()),
            "enlarge_small": bool(self.enlarge_cb.get()),
            "margins": {
                "top": float(self.m_top.get() or 0),
                "left": float(self.m_left.get() or 0),
                "bottom": float(self.m_bottom.get() or 0),
                "right": float(self.m_right.get() or 0),
            },
            "position": "centered" if "Ortala" in self.pos_seg.get() else "topleft",
            "use_exif": bool(self.exif_cb.get()),
            "color_mode": self.color_mode.get(),
            "limit_dpi": dpi_val,
            "is_single_pdf": "Tek" in self.out_type.get(),
            "single_pdf_name": self.pdf_name.get() or "Belge.pdf",
            "output_folder": self.out_folder.get(),
        }
        self.on_start_convert(opts)


class PdfToImageApp(ctk.CTkFrame):
    def __init__(self, master, on_start_convert):
        super().__init__(master, fg_color="transparent")
        self.on_start_convert = on_start_convert
        self.pdf_files = []

        bar = ctk.CTkFrame(self, height=40, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(bar, text="PDF Dönüştürücü", font=("Segoe UI", 16, "bold"), text_color="#FFFFFF").pack(side="left", padx=4)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="#181B22", corner_radius=16)
        self.scroll.pack(fill="both", expand=True, padx=2, pady=2)

        tb = ctk.CTkFrame(self.scroll, fg_color="transparent")
        tb.pack(fill="x", pady=4)
        ctk.CTkButton(tb, text="+ PDF Ekle", width=85, height=28, fg_color="#1976D2", hover_color="#1565C0", command=self.pick_pdfs).pack(side="left", padx=2)
        ctk.CTkButton(tb, text="+ Klasör", width=75, height=28, fg_color="#0288D1", hover_color="#0277BD", command=self.pick_pdf_folder).pack(side="left", padx=2)
        ctk.CTkButton(tb, text="Temizle", width=65, height=28, fg_color="#D32F2F", hover_color="#B71C1C", command=self.clear_pdfs).pack(side="left", padx=2)

        self.list_box = ctk.CTkTextbox(self.scroll, height=130, corner_radius=8, font=("Consolas", 10))
        self.list_box.pack(fill="x", pady=6)

        ctk.CTkLabel(self.scroll, text="Dönüştürülecek Format", font=("Segoe UI", 12, "bold"), text_color="#90CAF9").pack(anchor="w", pady=(8, 2))
        self.fmt_seg = ctk.CTkSegmentedButton(self.scroll, values=["JPG", "PNG", "BMP", "GIF", "TIF"])
        self.fmt_seg.set("JPG")
        self.fmt_seg.pack(fill="x", pady=4)

        ctk.CTkLabel(self.scroll, text="Render DPI & Kayıt Yolu", font=("Segoe UI", 12, "bold"), text_color="#90CAF9").pack(anchor="w", pady=(8, 2))
        self.dpi_entry = ctk.CTkEntry(self.scroll, placeholder_text="Render DPI", height=28)
        self.dpi_entry.insert(0, "200")
        self.dpi_entry.pack(fill="x", pady=3)
        ToolTip(self.dpi_entry, "DPI Boyut Ayarı")

        out_f_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        out_f_row.pack(fill="x", pady=2)
        self.out_folder = ctk.CTkEntry(out_f_row, placeholder_text="Kayıt Klasörü (Varsayılan: PDF Dizini)", height=28)
        self.out_folder.pack(side="left", fill="x", expand=True, padx=2)
        ctk.CTkButton(out_f_row, text="📁", width=34, height=28, command=self.pick_out_folder).pack(side="left", padx=2)

        ctk.CTkButton(
            self.scroll, text="GÖRSELLERE DÖNÜŞTÜR", font=("Segoe UI", 13, "bold"),
            fg_color="#1565C0", hover_color="#0D47A1", height=42, corner_radius=12,
            command=self.dispatch_convert
        ).pack(fill="x", pady=(18, 10))

    def pick_pdfs(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF Dosyaları", "*.pdf")])
        if files:
            for f in files:
                if f not in self.pdf_files:
                    self.pdf_files.append(f)
            self.refresh_list()

    def pick_pdf_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            for f in os.listdir(folder):
                if f.lower().endswith(".pdf"):
                    p = os.path.join(folder, f)
                    if p not in self.pdf_files:
                        self.pdf_files.append(p)
            self.refresh_list()

    def clear_pdfs(self):
        self.pdf_files.clear()
        self.refresh_list()

    def refresh_list(self):
        self.list_box.delete("1.0", "end")
        for p in self.pdf_files:
            self.list_box.insert("end", os.path.basename(p) + "\n")

    def pick_out_folder(self):
        f = filedialog.askdirectory()
        if f:
            self.out_folder.delete(0, "end")
            self.out_folder.insert(0, f)

    def dispatch_convert(self):
        try:
            dpi_val = int(float(self.dpi_entry.get().strip()))
        except Exception:
            dpi_val = 200

        opts = {
            "pdf_paths": self.pdf_files,
            "format": self.fmt_seg.get(),
            "dpi": dpi_val,
            "output_folder": self.out_folder.get()
        }
        self.on_start_convert(opts)