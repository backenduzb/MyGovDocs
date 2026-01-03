from django.shortcuts import render, get_object_or_404, redirect
from .models import Document
from .forms import CaptchaForm
from django.conf import settings

def access_doc(request, pk):
    doc = get_object_or_404(Document, document_code=pk)
    error = None

    session_key = f'captcha_passed_{pk}'
    captcha_passed = request.session.get(session_key, False)

    # if settings.DEBUG:
    #     return render(request, 'documents/view.html', {
    #                 'doc': doc,
    #                 'pdf_preview': doc.pdf_image.url
    #             })  

    if not captcha_passed:
        if request.method == 'POST':
            form = CaptchaForm(request.POST)
            if form.is_valid():
                request.session[session_key] = True
                request.session.pop(session_key, None)
                return render(request, 'documents/view.html', {
                    'doc': doc,
                    'pdf_preview': doc.pdf_image.url
                })  
        return render(request, 'documents/access.html', {
            'captcha_passed': False
        })
    return render(request, 'documents/access.html', {
        'captcha_passed': True,
        'error': error
    })
