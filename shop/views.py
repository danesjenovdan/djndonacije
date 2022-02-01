from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core import signing
#from .payments_braintree import client_token

import json

from . import models, qrcode

from datetime import datetime
from wkhtmltopdf.views import PDFTemplateResponse

def index(requst):
    return HttpResponse("")


@csrf_exempt
def poloznica(request):
    data = json.loads(request.body.decode('utf8'))
    bill = {}
    bill['id'] = data.get('id')
    bill['date'] = data.get('date')
    bill['price'] = data.get('price')
    bill['referencemath'] = data.get('reference')
    bill['code'] = data.get('code')
    bill['purpose'] = data.get('purpose')

    victim = {}
    victim['name'] = data.get('name')
    victim['address1'] = data.get('address1')
    victim['address2'] = data.get('address2')

    qr_code = qrcode.generate_upn_qr(victim['name'],
                                     victim['address1'],
                                     victim['address2'],
                                     float(bill['price']),
                                     bill['referencemath'],
                                     bill['purpose'])

    qr_code = "\n".join(qr_code.split("\n")[2:])

    return render('poloznica.html', {'victim': victim,
                                                 'bill': bill,
                                                 'upn_id': data.get('upn_id'),
                                                 'qr_code': qr_code})


def getPDFodOrder(request, pk):
    try:
        order = get_object_or_404(models.Order, pk=signing.loads(pk))
    except:
        order = models.Order.objects.first()

    bill = {}
    bill['id'] = order.id
    bill['date'] = datetime.now().strftime('%d.%m.%Y')
    bill['price'] = order.basket.total
    bill['referencemath'] = order.payment_id

    if order.is_donation():
        bill['code'] = "ADCS"
        bill['purpose'] = "Donacija"
    else:
        bill['code'] = "GDSV"
        bill['purpose'] = "Položnica za naročilo št. " + str(order.id)

    address = order.address.split(',')

    victim = {}
    victim['name'] = order.name
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
