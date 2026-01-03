import fitz
import qrcode
import os

from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib import admin
from django.urls import reverse

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    readonly_fields = ('guid', 'created')
    fields = (
        'file',
        'guid',
        'pin',
        'have_qr'
    )

    def save_model(self, request, obj, form, change):
        old_obj = None
        if change:
            old_obj = Document.objects.filter(pk=obj.pk).first()

        super().save_model(request, obj, form, change)

        if old_obj and old_obj.file == obj.file and old_obj.guid == obj.guid:
            return

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

        if not obj.file:
            obj.save(update_fields=['qr'])
            return

        pdf_path = obj.file.path
        doc = fitz.open(pdf_path)
        page = doc[-1]

        w, h = page.rect.width, page.rect.height

        if obj.have_qr:
            images = page.get_images(full=True)

            if images:
                xref = images[-1][0]
                rects = page.get_image_rects(xref)

                if rects:
                    old_rect = rects[0]

                    page.draw_rect(old_rect, fill=(1, 1, 1),color=None)

                    size = min(old_rect.width, old_rect.height)
                    new_size = size * 1.03

                    qr_rect = fitz.Rect(
                        old_rect.x0,
                        old_rect.y0,
                        old_rect.x0 + new_size,
                        old_rect.y0 + new_size
                    )

                    page.insert_image(qr_rect, stream=qr_bytes)

                    blocks = page.get_text("dict")["blocks"]

                    for b in blocks:
                        if b["type"] == 0:
                            for line in b["lines"]:
                                for span in line["spans"]:
                                    if abs(span["size"] - 22.5) < 0.5:
                                        text_rect = fitz.Rect(span["bbox"])
                                        page.draw_rect(text_rect, fill=(1, 1, 1), color=None)
                                        page.insert_text(
                                            fitz.Point(text_rect.x0, text_rect.y1),
                                            obj.pin,
                                            fontsize=22.5,
                                            fontname="helv",
                                            color=(0, 0, 0)
                                        )
                                        break
            else:
                obj.have_qr = False 

        if not obj.have_qr:
            size = 120
            qr_rect = fitz.Rect(
                w - size - 40,
                h - size - 40,
                w - 40,
                h - 40
            )

            page.insert_image(qr_rect, stream=qr_bytes)

            page.insert_text(
                fitz.Point(qr_rect.x0 - 70, qr_rect.y1 - 50),
                f"{obj.pin}",
                fontsize=22.5,
                fontname="helv",
                color=(0, 0, 0)
            )

        tmp = pdf_path.replace('.pdf', '_tmp.pdf')
        doc.save(tmp, garbage=4, deflate=True)
        doc.close()
        os.replace(tmp, pdf_path)

        obj.save(update_fields=['qr', 'have_qr'])
