import os
import uuid
from io import BytesIO

import fitz
import qrcode
from django.contrib import admin
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .forms import DocumentAdminForm
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    form = DocumentAdminForm
    readonly_fields = ("guid", "created", "qr_preview", "pdf_editor")
    fields = (
        "file",
        "guid",
        "pin",
        "qr_page",
        "qr_preview",
        "pdf_editor",
        "qr_x",
        "qr_y",
        "qr_scale",
        "pin_x",
        "pin_y",
        "pin_font_size",
        "created",
    )

    class Media:
        css = {"all": ("admin/document_editor.css",)}
        js = ("admin/document_editor.js",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/preview/",
                self.admin_site.admin_view(self.preview_image_view),
                name="document_preview_image",
            ),
        ]
        return custom_urls + urls

    def preview_image_view(self, request, object_id):
        obj = Document.objects.get(pk=object_id)

        if not obj.file:
            return HttpResponse(status=404)

        doc = fitz.open(obj.file.path)
        page_index = max(0, min(obj.qr_page - 1, len(doc) - 1))
        page = doc[page_index]
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        img_bytes = pix.tobytes("png")
        doc.close()

        return HttpResponse(img_bytes, content_type="image/png")

    def qr_preview(self, obj):
        if obj and obj.qr:
            return format_html('<img src="{}" width="180" />', obj.qr.url)
        return "QR hali yaratilmagan"

    qr_preview.short_description = "QR kod"

    def pdf_editor(self, obj):
        if not obj or not obj.pk or not obj.file:
            return "Avval faylni saqlang, keyin preview chiqadi."

        preview_url = reverse("admin:document_preview_image", args=[obj.pk])
        qr_url = obj.qr.url if obj and obj.qr else ""

        html = f"""
        <div class="pdf-editor-root"
             data-preview-url="{preview_url}"
             data-qr-x="{obj.qr_x}"
             data-qr-y="{obj.qr_y}"
             data-qr-scale="{obj.qr_scale}"
             data-pin-x="{obj.pin_x}"
             data-pin-y="{obj.pin_y}"
             data-pin-font="{obj.pin_font_size}"
             data-pin="{obj.pin}">

            <div class="pdf-editor-toolbar">
                <label class="slider-control">
                    <span class="slider-control-label">QR scale:</span>
                    <div class="slider-value-row">
                        <input
                            type="range"
                            min="0.05"
                            max="0.4"
                            step="0.01"
                            value="{obj.qr_scale}"
                            id="qr-scale-slider">
                        <span id="qr-scale-value" class="slider-value">0%</span>
                    </div>
                </label>
                <label class="slider-control">
                    <span class="slider-control-label">PIN size:</span>
                    <div class="slider-value-row">
                        <input
                            type="range"
                            min="8"
                            max="40"
                            step="0.5"
                            value="{obj.pin_font_size}"
                            id="pin-font-slider">
                        <span id="pin-font-value" class="slider-value">0%</span>
                    </div>
                </label>
            </div>

            <div class="pdf-editor-stage" id="pdf-editor-stage">
                <img src="{preview_url}" id="pdf-preview-image" class="pdf-preview-image" />

                <div id="qr-box" class="draggable qr-box">
                    {f'<img src="{qr_url}" alt="QR" />' if qr_url else '<div class="qr-box-inner">QR yo\'q</div>'}
                </div>

                <div id="pin-box" class="draggable pin-box">{obj.pin}</div>
            </div>
        </div>
        """
        return mark_safe(html)

    pdf_editor.short_description = "PDF preview editor"

    def save_model(self, request, obj, form, change):
        old_obj = None
        if change:
            old_obj = Document.objects.filter(pk=obj.pk).first()
    
        new_uploaded_file = bool(form.cleaned_data.get("file"))
    
        super().save_model(request, obj, form, change)
    
        file_changed = False
        if not old_obj:
            file_changed = True
        elif new_uploaded_file:
            file_changed = True
        elif old_obj and old_obj.file.name != obj.file.name:
            file_changed = True
    
        if obj.file and (not obj.source_file or file_changed):
            obj.file.open("rb")
            original_bytes = obj.file.read()
            obj.file.close()
    
            source_name = f"source_{os.path.basename(obj.file.name)}"
            obj.source_file.save(
                source_name,
                ContentFile(original_bytes),
                save=False,
            )
            obj.save(update_fields=["source_file"])
    
        url = request.build_absolute_uri(
            reverse("doc-access") + f"?guid={obj.guid}"
        ).replace("http://", "https://")
    
        qr_img = qrcode.make(url)
        qr_buf = BytesIO()
        qr_img.save(qr_buf, format="PNG")
        qr_bytes = qr_buf.getvalue()
    
        obj.qr.save(
            f"doc_{obj.guid}.png",
            ContentFile(qr_bytes),
            save=False
        )
    
        self._render_pdf_with_qr(obj, randomize_file_name=(change and file_changed))
    
        obj.save(update_fields=["qr", "file"])
        
    def _render_pdf_with_qr(self, obj, randomize_file_name=False):
        if not obj.source_file or not obj.qr:
            return
    
        try:
            doc = fitz.open(obj.source_file.path)
        except Exception:
            return
    
        try:
            page_index = max(0, min((obj.qr_page or 1) - 1, len(doc) - 1))
            page = doc[page_index]
            width = page.rect.width
            height = page.rect.height
    
            def clamp(value, minimum, maximum):
                return max(minimum, min(maximum, value))
    
            qr_scale = max(obj.qr_scale or 0.14, 0.01)
            qr_size = min(width, height) * qr_scale
    
            qr_x = clamp((obj.qr_x or 0) * width, 0, max(0, width - qr_size))
            qr_y = clamp((obj.qr_y or 0) * height, 0, max(0, height - qr_size))
    
            qr_rect = fitz.Rect(qr_x, qr_y, qr_x + qr_size, qr_y + qr_size)
    
            if os.path.exists(obj.qr.path):
                page.insert_image(qr_rect, filename=obj.qr.path, overlay=True)
    
            text = (obj.pin or "").strip()
            if text:
                pin_font = max(float(obj.pin_font_size or 22.5), 6)
    
                pad_x = 6
                pad_y = 4
    
                text_width = fitz.get_text_length(text, fontname="helv", fontsize=pin_font)
                text_height = pin_font * 1.2
    
                box_width = text_width + (pad_x * 2)
                box_height = text_height + (pad_y * 2)
    
                pin_left = clamp((obj.pin_x or 0) * width, 0, max(0, width - box_width))
                pin_top = clamp((obj.pin_y or 0) * height, 0, max(0, height - box_height))
    
                pin_rect = fitz.Rect(
                    pin_left,
                    pin_top,
                    pin_left + box_width,
                    pin_top + box_height,
                )
    
                page.draw_rect(
                    pin_rect,
                    color=(1, 1, 1),
                    fill=(1, 1, 1),
                    overlay=True,
                )
    
                text_point = fitz.Point(
                    pin_left + pad_x,
                    pin_top + pad_y + pin_font
                )
    
                page.insert_text(
                    text_point,
                    text,
                    fontname="helv",
                    fontsize=pin_font,
                    color=(0, 0, 0),
                    overlay=True,
                )
    
            pdf_bytes = doc.write()
        finally:
            doc.close()
    
        original_name = os.path.basename(obj.source_file.name or obj.file.name or "document.pdf")
        base_name, ext = os.path.splitext(original_name)
    
        if not ext:
            ext = ".pdf"
    
        if randomize_file_name:
            dest_name = f"{uuid.uuid4().hex}{ext}"
        else:
            dest_name = f"{base_name}{ext}"
    
        old_name = obj.file.name if obj.file else None
    
        if old_name and old_name != dest_name:
            storage = obj.file.storage
            if storage.exists(old_name):
                storage.delete(old_name)
    
        obj.file.save(dest_name, ContentFile(pdf_bytes), save=False)