import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import FileResponse
from .models import Document


def access_doc(request):
    guid = request.GET.get('guid')
    obj = get_object_or_404(Document, guid=guid)

    captcha_passed = request.session.get('captcha_passed', False)

    if request.method == "POST":

        if not captcha_passed:
            token = request.POST.get("g-recaptcha-response")

            data = {
                "secret": settings.RECAPTCHA_PRIVATE_KEY,
                "response": token
            }

            r = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data=data
            )
            result = r.json()

            if result.get("success"):
                request.session["captcha_passed"] = True
                captcha_passed = True
            else:
                return render(request, "documents/access.html", {
                    "captcha": settings.RECAPTCHA_PUBLIC_KEY
                })

        else:
            pin = request.POST.get("pin")

            if pin == obj.pin:
                request.session["captcha_passed"] = False

                return FileResponse(
                    obj.file.open("rb"),
                    as_attachment=True,
                    filename=obj.file.name.split("/")[-1]
                )

            return render(request, "documents/access.html", {
                "captcha_passed": True,
                "error": "Неправильный ПИН код"
            })

    return render(request, "documents/access.html", {
        "captcha_passed": captcha_passed,
        "captcha": settings.RECAPTCHA_PUBLIC_KEY
    })