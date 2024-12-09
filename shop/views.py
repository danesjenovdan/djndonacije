import json
from datetime import datetime

from django.core import signing
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from sentry_sdk import capture_exception
from wkhtmltopdf.views import PDFTemplateResponse

from . import models
from .qrcode import UPNQRException, generate_upnqr_svg

# from .payments_braintree import client_token





def index(requst):
    return HttpResponse("")


@csrf_exempt
def poloznica(request):
    data = json.loads(request.body.decode("utf8"))
    bill = {}
    bill["id"] = data.get("id")
    bill["date"] = data.get("date")
    bill["price"] = data.get("price")
    bill["referencemath"] = data.get("reference")
    bill["code"] = data.get("code")
    bill["purpose"] = data.get("purpose")

    victim = {}
    victim["name"] = data.get("name")
    victim["address1"] = data.get("address1")
    victim["address2"] = data.get("address2")

    try:
        qr_code = generate_upnqr_svg(
            name=victim["name"],
            address1=victim["address1"],
            address2=victim["address2"],
            amount=float(bill["price"]),
            code=bill["code"],
            purpose=bill["purpose"],
            reference=bill["referencemath"],
        )
    except UPNQRException as e:
        capture_exception(e)
        qr_code = None

    return render(
        "poloznica.html",
        {
            "victim": victim,
            "bill": bill,
            "upn_id": data.get("upn_id"),
            "qr_code": qr_code,
        },
    )


def getPDFodOrder(request, pk):
    try:
        order = get_object_or_404(models.Order, pk=signing.loads(pk))
    except:
        order = models.Order.objects.first()

    bill = {}
    bill["id"] = order.id
    bill["date"] = datetime.now().strftime("%d.%m.%Y")
    bill["price"] = order.basket.total
    bill["referencemath"] = order.payment_id

    if order.is_donation():
        bill["code"] = "ADCS"
        bill["purpose"] = "Donacija"
    else:
        bill["code"] = "GDSV"
        bill["purpose"] = "Položnica za naročilo št. " + str(order.id)

    address = order.address.split(",")

    victim = {}
    victim["name"] = order.name
    victim["address1"] = address[0]
    victim["address2"] = address[1] if len(address) > 1 else ""

    try:
        qr_code = generate_upnqr_svg(
            name=victim["name"],
            address1=victim["address1"],
            address2=victim["address2"],
            amount=bill["price"],
            code=bill["code"],
            purpose=bill["purpose"],
            reference=bill["referencemath"],
        )
    except UPNQRException as e:
        capture_exception(e)
        qr_code = None

    return PDFTemplateResponse(
        request=request,
        template="poloznica.html",
        filename="upn_djnd.pdf",
        context={"victim": victim, "bill": bill, "pdf": True, "qr_code": qr_code},
        show_content_in_browser=True,
    )
