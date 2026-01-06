from django.db import models
from string import digits
from random import choices
import uuid

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
    qr = models.ImageField(upload_to='qr/', blank=True)
    
    guid = models.CharField(
        max_length=40,
        unique=True,
        editable=False,
        default=guid_generator
    )
    have_qr = models.BooleanField(default=True)
    pin = models.CharField(max_length=4, default=generate_pin)
    
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Doc #{self.guid}"
