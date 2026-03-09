from django import forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from .models import Document

class CaptchaForm(forms.Form):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

class DocumentAdminForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = '__all__'
        widgets = {
            'qr_x': forms.HiddenInput(),
            'qr_y': forms.HiddenInput(),
            'qr_scale': forms.HiddenInput(),
            'pin_x': forms.HiddenInput(),
            'pin_y': forms.HiddenInput(),
            'pin_font_size': forms.HiddenInput(),
            'source_file': forms.HiddenInput(),
            'qr': forms.HiddenInput(),
        }