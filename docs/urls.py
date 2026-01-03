from django.urls import path
from .views import access_doc

urlpatterns = [
    path('file/download/', access_doc, name='doc-access'),
]
