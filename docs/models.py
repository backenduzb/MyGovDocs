from django.db import models
from django.core.files.base import ContentFile
from string import digits
from random import choices
import uuid
import os


def generate_pin():
    return ''.join(choices(digits, k=4))


def guid_generator():
    raw = uuid.uuid4().hex
    return "-".join([
        raw[0:4],
        raw[4:8],
        raw[8:12],
        raw[12:16],
        raw[16:20],
        raw[20:24],
        raw[24:28],
    ])


class Document(models.Model):
    file = models.FileField(upload_to='docs/')
    source_file = models.FileField(upload_to='docs/source/', blank=True, editable=False)
    qr = models.ImageField(upload_to='qr/', blank=True)

    guid = models.CharField(
        max_length=40,
        unique=True,
        editable=False,
        default=guid_generator
    )
    pin = models.CharField(max_length=4, default=generate_pin)

    qr_x = models.FloatField(default=0.78)
    qr_y = models.FloatField(default=0.78)
    qr_scale = models.FloatField(default=0.14)

    pin_x = models.FloatField(default=0.68)
    pin_y = models.FloatField(default=0.92)
    pin_font_size = models.FloatField(default=22.5)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Doc #{self.guid}"