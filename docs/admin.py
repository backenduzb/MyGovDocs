import os
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
                <label>QR scale:
                    <input type="range" min="0.05" max="0.4" step="0.01" value="{obj.qr_scale}" id="qr-scale-slider">
                </label>
                <label>PIN size:
                    <input type="range" min="8" max="40" step="0.5" value="{obj.pin_font_size}" id="pin-font-slider">
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

        super().save_model(request, obj, form, change)

        file_changed = False
        if old_obj and old_obj.file != obj.file:
            file_changed = True
        if not old_obj:
            file_changed = True

        if obj.file and (not obj.source_file or file_changed):
            obj.file.open("rb")
            original_bytes = obj.file.read()
            obj.file.close()

            obj.source_file.save(
                f"source_{os.path.basename(obj.file.name)}",
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

        obj.qr.save(f"doc_{obj.guid}.png", ContentFile(qr_bytes), save=False)

        obj.save(update_fields=["qr"])
