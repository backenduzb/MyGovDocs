from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse
from django.utils.text import TruncateHTMLParser
from .models import Document

def access_doc(request):
    guid = request.GET.get('guid')
    obj = get_object_or_404(Document, guid=guid)
    
    
    return render(
        request, 'documents/access.html',{'message':'salom'}
    )
    # return FileResponse(
    #     obj.file.open('rb'),
    #     as_attachment=True,
    #     filename=obj.file.name.split('/')[1]
    # )