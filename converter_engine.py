import os
import io
from PIL import Image, ImageOps
import pymupdf


class ConverterEngine:
    @staticmethod
    def get_unit_factor(unit: str) -> float:
        unit = unit.lower()
        if "inç" in unit or "inch" in unit:
            return 72.0
        elif "cm" in unit:
            return 72.0 / 2.54
        elif "mm" in unit:
            return 72.0 / 25.4
        return 72.0

    @classmethod
    def convert_images_to_pdf(cls, images: list[str], options: dict, progress_cb=None) -> list[str]:
        if not images:
            raise ValueError("Lütfen en az bir görsel ekleyin.")

        unit_factor = cls.get_unit_factor(options.get("unit", "inches"))
        margins = options.get("margins", {"top": 0.0, "left": 0.0, "bottom": 0.0, "right": 0.0})
        top_m = margins["top"] * unit_factor
        left_m = margins["left"] * unit_factor
        bottom_m = margins["bottom"] * unit_factor
        right_m = margins["right"] * unit_factor

        page_mode = options.get("page_size_mode", "match")
        target_dpi = max(30.0, float(options.get("limit_dpi") or 100))
        is_single_pdf = options.get("is_single_pdf", True)
        output_folder = options.get("output_folder", "") or os.path.dirname(images[0])

        single_pdf_name = options.get("single_pdf_name", "Belge.pdf")
        if not single_pdf_name.lower().endswith(".pdf"):
            single_pdf_name += ".pdf"

        generated_files = []

        def build_pdf(img_list, target_path):
            doc = pymupdf.open()
            for idx, img_path in enumerate(img_list):
                with Image.open(img_path) as raw_img:
                    if options.get("use_exif", True):
                        raw_img = ImageOps.exif_transpose(raw_img) or raw_img

                    orig_w, orig_h = raw_img.size

                    if "özel" in page_mode.lower() or "specify" in page_mode.lower():
                        page_w = options.get("spec_width", 8.5) * unit_factor
                        page_h = options.get("spec_height", 11.0) * unit_factor
                        avail_w = max(1.0, page_w - left_m - right_m)
                        avail_h = max(1.0, page_h - top_m - bottom_m)

                        ratio_img = orig_w / orig_h
                        ratio_avail = avail_w / avail_h
                        if ratio_img > ratio_avail:
                            target_pt_w = avail_w
                            target_pt_h = avail_w / ratio_img
                        else:
                            target_pt_h = avail_h
                            target_pt_w = avail_h * ratio_img

                        if options.get("position", "centered") == "centered":
                            pos_x = left_m + (avail_w - target_pt_w) / 2.0
                            pos_y = top_m + (avail_h - target_pt_h) / 2.0
                        else:
                            pos_x = left_m
                            pos_y = top_m

                        rect = pymupdf.Rect(pos_x, pos_y, pos_x + target_pt_w, pos_y + target_pt_h)

                        target_px_w = max(1, int(round((target_pt_w / 72.0) * target_dpi)))
                        target_px_h = max(1, int(round((target_pt_h / 72.0) * target_dpi)))
                        proc_img = raw_img.resize((target_px_w, target_px_h), Image.Resampling.LANCZOS)
                    else:
                        img_pt_w = (orig_w / target_dpi) * 72.0
                        img_pt_h = (orig_h / target_dpi) * 72.0
                        page_w = img_pt_w + left_m + right_m
                        page_h = img_pt_h + top_m + bottom_m

                        pos_x = left_m
                        pos_y = top_m
                        rect = pymupdf.Rect(pos_x, pos_y, pos_x + img_pt_w, pos_y + img_pt_h)

                        if target_dpi < 300:
                            scale_factor = max(0.25, target_dpi / 300.0)
                            new_w = max(1, int(round(orig_w * scale_factor)))
                            new_h = max(1, int(round(orig_h * scale_factor)))
                            proc_img = raw_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                        else:
                            proc_img = raw_img.copy()

                    color_mode = options.get("color_mode", "Orijinal")
                    if color_mode == "CMYK":
                        proc_img = proc_img.convert("CMYK")
                    elif color_mode == "Siyah-Beyaz":
                        proc_img = proc_img.convert("L").point(lambda x: 0 if x < 128 else 255, "1")
                    else:
                        if proc_img.mode not in ("RGB", "RGBA"):
                            proc_img = proc_img.convert("RGB")

                    if target_dpi <= 100:
                        quality = 65
                    elif target_dpi <= 200:
                        quality = 78
                    elif target_dpi <= 350:
                        quality = 88
                    else:
                        quality = 96

                    buffer = io.BytesIO()
                    save_format = "JPEG" if color_mode in ("CMYK", "Orijinal") and proc_img.mode != "RGBA" else "PNG"
                    if proc_img.mode == "1":
                        save_format = "PNG"

                    if save_format == "JPEG":
                        if proc_img.mode == "RGBA":
                            proc_img = proc_img.convert("RGB")
                        proc_img.save(buffer, format="JPEG", quality=quality, optimize=True, dpi=(int(target_dpi), int(target_dpi)))
                    else:
                        proc_img.save(buffer, format=save_format, optimize=True, dpi=(int(target_dpi), int(target_dpi)))

                    page = doc.new_page(width=page_w, height=page_h)
                    page.insert_image(rect, stream=buffer.getvalue())

                    if progress_cb:
                        progress_cb(idx + 1, len(img_list))

            doc.save(target_path, garbage=4, deflate=True)
            doc.close()
            return target_path

        if is_single_pdf:
            out_file = os.path.join(output_folder, single_pdf_name)
            build_pdf(images, out_file)
            generated_files.append(out_file)
        else:
            for idx, img_path in enumerate(images):
                base_name = os.path.splitext(os.path.basename(img_path))[0]
                out_file = os.path.join(output_folder, f"{base_name}.pdf")
                build_pdf([img_path], out_file)
                generated_files.append(out_file)

        return generated_files

    @classmethod
    def convert_pdf_to_images(cls, pdf_paths: list[str], output_folder: str, fmt: str = "JPG",
                               dpi: int = 200, progress_cb=None) -> list[str]:
        if not pdf_paths:
            raise ValueError("Lütfen en az bir PDF seçin.")
        if not output_folder:
            output_folder = os.path.dirname(pdf_paths[0])

        fmt = fmt.lower().strip(".")
        output_images = []
        total = len(pdf_paths)

        for p_idx, pdf_path in enumerate(pdf_paths):
            doc = pymupdf.open(pdf_path)
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            zoom = dpi / 72.0
            mat = pymupdf.Matrix(zoom, zoom)

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=mat, alpha=False)

                out_filename = f"{base_name}_sayfa_{page_num + 1}.{fmt}"
                out_path = os.path.join(output_folder, out_filename)

                if fmt in ("jpg", "jpeg"):
                    pix.save(out_path, output="jpeg")
                elif fmt == "png":
                    pix.save(out_path, output="png")
                else:
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    img.save(out_path, format=fmt.upper())

                output_images.append(out_path)

            doc.close()
            if progress_cb:
                progress_cb(p_idx + 1, total)

        return output_images