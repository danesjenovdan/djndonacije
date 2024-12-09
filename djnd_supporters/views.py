import csv
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from sentry_sdk import capture_exception
from wkhtmltopdf.views import PDFTemplateResponse

from djnd_supporters import models, utils
from djndonacije import payment
from shop.qrcode import UPNQRException, generate_upnqr_svg


class TestPaymentView(TemplateView):
    template_name = "test_payment.html"

    def get_context_data(self, *args, **kwargs):
        context = super(TestPaymentView, self).get_context_data(*args, **kwargs)
        context["token"] = payment.client_token()["token"]
        return context


class TestUPNView(TemplateView):
    template_name = "poloznica.html"

    def get_context_data(self, *args, **kwargs):
        context = super(TestUPNView, self).get_context_data(*args, **kwargs)
        context["qr_code"] = generate_upnqr_svg(
            name="Janez MojeImeJepredolgoInŠumnik Novak",
            address1="Ulica z zelo dolgim imenom, ki je predolg 1",
            address2="1000 Ljubljana-Domžale-Hrastnik-Dravlje",
            amount=Decimal("123.45"),
            # amount=123,
            # amount=123.45,
            iban="SI56 6100 0000 5740 710",
            # purpose=None,
            purpose="DonacijaDonacijaDonacijaDonacijaDonacijaDonacijaDonacijaDonacija",
            reference="SI00 0000008",
            code="ADCS",
            # unused={'1': TestUPNView},
        )
        # context['qr_code'] = None
        # print(context['qr_code'])
        return context


def getPDForDonation(request, pk):
    transaction = get_object_or_404(models.Transaction, pk=pk)

    bill = {}
    bill["id"] = transaction.id
    bill["date"] = datetime.now().strftime("%d.%m.%Y")
    bill["price"] = transaction.amount
    bill["referencemath"] = transaction.reference

    bill["code"] = "ADCS"
    bill["purpose"] = "Donacija"
    if transaction.campaign and transaction.campaign.upn_name:
        bill["purpose"] = transaction.campaign.upn_name

    address = transaction.subscriber.address.split(",")

    victim = {}
    victim["name"] = transaction.subscriber.name
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


@login_required
def braintree_export(request):
    last_month_bt_transactions = utils.export_bt()
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="bt_export.csv"'},
    )

    if not last_month_bt_transactions:
        return response

    writer = csv.DictWriter(response, fieldnames=last_month_bt_transactions[0].keys())
    writer.writeheader()
    writer.writerows(last_month_bt_transactions)

    return response
