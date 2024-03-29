from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from djnd_supporters import models, utils
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from djndonacije import payment
from datetime import datetime
from shop.qrcode import generate_upnqr_svg, UPNQRException
from wkhtmltopdf.views import PDFTemplateResponse
from decimal import Decimal
from sentry_sdk import capture_exception

from djnd_supporters.mautic_api import MauticApi
from djnd_supporters.forms import NewsletterForm

import csv

mautic_api = MauticApi()

class TestPaymentView(TemplateView):
    template_name = "test_payment.html"

    def get_context_data(self, *args, **kwargs):
        context = super(TestPaymentView, self).get_context_data(*args, **kwargs)
        context['token'] = payment.client_token()['token']
        return context


class TestUPNView(TemplateView):
    template_name = "poloznica.html"

    def get_context_data(self, *args, **kwargs):
        context = super(TestUPNView, self).get_context_data(*args, **kwargs)
        context['qr_code'] = generate_upnqr_svg(
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


class AddSegmentContacts(TemplateView):
    template_name = "add_segment_contacts.html"

    def get(self, request, slug):
        form = NewsletterForm()
        newsletter = models.Newsletter.objects.filter(slug=slug).first()

        return render(
            request,
            self.template_name,
            {"form": form, "newsletter": newsletter},
        )

    def post(self, request, slug):
        form = NewsletterForm(request.POST)
        newsletter = models.Newsletter.objects.filter(slug=slug).first()

        if form.is_valid():
            email = form.cleaned_data.get("email")
            response, response_status = mautic_api.getContactByEmail(email)
            if response_status == 200:
                contacts = response["contacts"]
                if contacts:
                    # if user already exists on mautic
                    mautic_id = list(contacts.keys())[0]
                    try:
                        # user exists on mautic and is connected to podpri
                        token = contacts[mautic_id]['fields']['core']['token']['value']
                    except:
                        # user exists on mautic and is not connected to podpri - create podpri Subscriber
                        subscriber = models.Subscriber.objects.create()
                        subscriber.save()
                        response, response_status = subscriber.save_to_mautic(email)

                    response, response_status = mautic_api.getSegmentsOfContact(mautic_id)
                    if response_status == 200:
                        segments = response['lists']
                        # če userja še ni na tem segmetu, ga dodamo, sicer samo vrnemo success
                        if segments and newsletter.segment not in segments.keys():
                            mautic_api.addContactToASegment(
                                newsletter.segment, mautic_id
                            )
                            # ne pošiljamo welcome maila, mogoče to ni okej
                        return render(
                            request,
                            self.template_name,
                            {"form": form, "newsletter": newsletter, "success": True},
                        )
                else:
                    # user does not exist on mautic, create new
                    subscriber = models.Subscriber.objects.create()
                    subscriber.save()
                    response, response_status = subscriber.save_to_mautic(email)
                    if response_status != 200:
                        # return error
                        return render(
                            request,
                            self.template_name,
                            {"form": form, "newsletter": newsletter, "error": response},
                        )
                    else:
                        # successfully subscribed
                        mautic_api.addContactToASegment(newsletter.segment, subscriber.mautic_id)
                        return render(
                            request,
                            self.template_name,
                            {"form": form, "newsletter": newsletter, "success": True},
                        )
            else:
                return render(
                    request,
                    self.template_name,
                    {"form": form, "newsletter": newsletter, "error": response},
                )

        return render(
            request,
            self.template_name,
            {"form": form, "newsletter": newsletter, "error": "Neveljaven elektronski naslov."},
        )


def getPDForDonation(request, pk):
    transaction = get_object_or_404(models.Transaction, pk=pk)

    bill = {}
    bill['id'] = transaction.id
    bill['date'] = datetime.now().strftime('%d.%m.%Y')
    bill['price'] = transaction.amount
    bill['referencemath'] = transaction.reference

    bill['code'] = "ADCS"
    bill['purpose'] = "Donacija"
    if transaction.campaign and transaction.campaign.upn_name:
        bill['purpose'] = transaction.campaign.upn_name

    address = transaction.subscriber.address.split(',')

    victim = {}
    victim['name'] = transaction.subscriber.name
    victim['address1'] = address[0]
    victim['address2'] = address[1] if len(address) > 1 else ''

    try:
        qr_code = generate_upnqr_svg(
            name=victim['name'],
            address1=victim['address1'],
            address2=victim['address2'],
            amount=bill['price'],
            code=bill['code'],
            purpose=bill['purpose'],
            reference=bill['referencemath'],
        )
    except UPNQRException as e:
        capture_exception(e)
        qr_code = None

    return PDFTemplateResponse(request=request,
                               template='poloznica.html',
                               filename='upn_djnd.pdf',
                               context={'victim': victim, 'bill': bill, 'pdf': True, 'qr_code': qr_code},
                               show_content_in_browser=True,
                               )


@login_required
def braintree_export(request):
    last_month_bt_transactions = utils.export_bt()
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="bt_export.csv"'},
    )

    if not  last_month_bt_transactions:
        return response

    writer = csv.DictWriter(response, fieldnames=last_month_bt_transactions[0].keys())
    writer.writeheader()
    writer.writerows(last_month_bt_transactions)

    return response
