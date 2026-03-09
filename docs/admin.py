import os
import fitz
import qrcode

from io import BytesIO
from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Document
from .forms import DocumentAdminForm


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    form = DocumentAdminForm
    readonly_fields = ('guid', 'created', 'qr_preview', 'pdf_editor')
    fields = (
        'file',
        'guid',
        'pin',
        'qr_page',
        'qr_preview',
        'pdf_editor',
        'qr_x',
        'qr_y',
        'qr_scale',
        'pin_x',
        'pin_y',
        'pin_font_size',
        'created',
    )

    class Media:
        css = {
            'all': ('admin/document_editor.css',)
        }
        js = ('admin/document_editor.js',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/preview/',
                self.admin_site.admin_view(self.preview_image_view),
                name='document_preview_image'
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

        return HttpResponse(img_bytes, content_type='image/png')

    def qr_preview(self, obj):
        if obj and obj.qr:
            return format_html('<img src="{}" width="180" />', obj.qr.url)
        return "QR hali yaratilmagan"
    qr_preview.short_description = "QR kod"

    def pdf_editor(self, obj):
        if not obj or not obj.pk or not obj.file:
            return "Avval faylni saqlang, keyin preview chiqadi."

        preview_url = reverse('admin:document_preview_image', args=[obj.pk])

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
                    <div class="qr-box-inner">QR</div>
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
            obj.file.open('rb')
            original_bytes = obj.file.read()
            obj.file.close()

            obj.source_file.save(
                f"source_{os.path.basename(obj.file.name)}",
                ContentFile(original_bytes),
                save=False
            )
            obj.save(update_fields=['source_file'])

        url = request.build_absolute_uri(
            reverse('doc-access') + f'?guid={obj.guid}'
        ).replace('http://', 'https://')

        qr_img = qrcode.make(url)
        qr_buf = BytesIO()
        qr_img.save(qr_buf, format='PNG')
        qr_bytes = qr_buf.getvalue()

        obj.qr.save(
            f'doc_{obj.guid}.png',
            ContentFile(qr_bytes),
            save=False
        )

        if not obj.source_file or not obj.file:
            obj.save(update_fields=['qr'])
            return

        source_pdf_path = obj.source_file.path
        output_pdf_path = obj.file.path

        doc = fitz.open(source_pdf_path)
        page_index = max(0, min(obj.qr_page - 1, len(doc) - 1))
        page = doc[page_index]

        w, h = page.rect.width, page.rect.height

        qr_size = min(w, h) * obj.qr_scale
        qr_x = w * obj.qr_x
        qr_y = h * obj.qr_y

        qr_rect = fitz.Rect(
            qr_x,
            qr_y,
            qr_x + qr_size,
            qr_y + qr_size
        )
        page.insert_image(qr_rect, stream=qr_bytes)

        pin_x = w * obj.pin_x
        pin_y = h * obj.pin_y

        page.insert_text(
            fitz.Point(pin_x, pin_y),
            str(obj.pin),
            fontsize=obj.pin_font_size,
            fontname="helv",
            color=(0, 0, 0)
        )

        base, ext = os.path.splitext(output_pdf_path)
        tmp = f"{base}_tmp{ext}"

        doc.save(tmp, garbage=4, deflate=True)
        doc.close()

        os.replace(tmp, output_pdf_path)

        obj.save(update_fields=['qr'])