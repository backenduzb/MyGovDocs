from django.shortcuts import render, get_object_or_404
from django.http import FileResponse
from .models import Document

def access_doc(request):
    guid = request.GET.get('guid')
    obj = get_object_or_404(Document, guid=guid)
    
    if request.POST:
        pin = request.POST.get('pin')
        if pin == obj.pin:
            return FileResponse(
                obj.file.open('rb'),
                as_attachment=True,
                filename=obj.file.name.split('/')[1]
            )
        else:
            return render(
                request, 'documents/access.html',{'error':'Неправильный ПИН код'}
            )

    return render(
        request, 'documents/access.html',{'message':'salom'}
    )
    