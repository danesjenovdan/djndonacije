from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import TemplateView
from djnd_supporters import models
from djndonacije import payment
from datetime import datetime
from shop import qrcode
from wkhtmltopdf.views import PDFTemplateResponse

class TestPaymentView(TemplateView):
    template_name = "test_payment.html"

    def get_context_data(self, *args, **kwargs):
        context = super(TestPaymentView, self).get_context_data(*args, **kwargs)
        context['token'] = payment.client_token()['token']
        return context


def getPDForDonation(request, pk):
    donation = get_object_or_404(models.Donation, pk=pk)

    bill = {}
    bill['id'] = donation.id
    bill['date'] = datetime.now().strftime('%d.%m.%Y')
    bill['price'] = donation.amount
    bill['referencemath'] = donation.reference

    bill['code'] = "ADCS"
    bill['purpose'] = "Donacija"

    address = donation.subscriber.address.split(',')

    victim = {}
    victim['name'] = donation.subscriber.name
    victim['address1'] = address[0]
    victim['address2'] = address[1] if len(address) > 1 else ''

    qr_code = qrcode.generate_upn_qr(victim['name'],
                                     victim['address1'],
                                     victim['address2'],
                                     bill['price'],
                                     bill['referencemath'],
                                     bill['purpose'])
    qr_code = "\n".join(qr_code.split("\n")[2:])

    return PDFTemplateResponse(request=request,
                               template='poloznica.html',
                               filename='upn_djnd.pdf',
                               context={'victim': victim, 'bill': bill, 'pdf': True, 'qr_code': qr_code},
                               show_content_in_browser=True,
                               )
