from django.http import JsonResponse
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from django.conf import settings
from django.core import signing
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.html import strip_tags

from rest_framework.views import APIView
from rest_framework import status

from datetime import datetime

from shop.models import Article, Basket, Order, Category, Item
from shop.serializers import ArticleSerializer, CategorySerializer, ItemSerializer
from shop.utils import get_basket, get_basket_data, add_article_to_basket, update_stock, update_basket

from djndonacije import payment
from djndonacije.slack_utils import send_slack_msg

from djnd_supporters.mautic_api import MauticApi
from djnd_supporters.models import Subscriber

from shop.views import getPDFodOrder
from shop.spam_mailer import send_mail_spam

import json
# Create your views here.

mautic_api = MauticApi()

def prepare_upn_data(order):
    ref = 'SI00 ' + str(order.id).zfill(10)
    order.payment_id=ref
    order.save()
    items = order.basket.items.all()
    update_stock(order)
    return ref

class ProductsList(APIView):
    def get(self, request, pk=None, format=None):
        if pk:
            product = get_object_or_404(Article, pk=pk)
            serializer = ArticleSerializer(product)
            return Response(serializer.data)
        else:
            articles = [article for article in Article.objects.filter(variant_of=None) if article.get_stock > 0]
            serializer = ArticleSerializer(articles, many=True)
            return Response(serializer.data)


class CategoryList(APIView):
    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class ItemView(APIView):
    def get_object(self, pk):
        try:
            return Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        basket = get_basket(request)
        items = basket.items.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        item = self.get_object(pk)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            basket = get_basket(request)
            update_basket(basket)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        item = self.get_object(pk)
        item.delete()
        basket = get_basket(request)
        update_basket(basket)
        return Response(status=status.HTTP_204_NO_CONTENT)


@csrf_exempt
def add_to_basket(request):
    if request.method == 'POST':
        basket = get_basket(request)
        try:
            data = json.loads(request.body.decode('utf-8'))
            product_id = data['product_id']
            quantity = data['quantity']
        except:
            return JsonResponse({"msg": "Json isn't valid"})
        article = get_object_or_404(Article, id=product_id)

        add_article_to_basket(basket, article, quantity)

        basket_data = get_basket_data(basket)
        html_from_view, count = get_items_for_basket(request)
        basket_data['items'] = html_from_view
        basket_data['item_count'] = count

        return JsonResponse(basket_data)
    else:
        return JsonResponse({"msg": "Method \"GET\" not allowed"})

def basket(request):
    basket = get_basket(request)
    basket_data = get_basket_data(basket)
    return JsonResponse(basket_data)


class Checkout(APIView):
    """
    address
    name
    phone
    email

    """
    def post(self, request, format=None):
        basket = get_basket(request)
        if not basket.items.all():
            return Response(
                {
                    'status': 'error',
                    'msg': 'Your basket is empty'
                },
                status=status.HTTP_400_BAD_REQUEST)
        basket.is_open = False
        basket.save()
        data = json.loads(request.body.decode('utf-8'))

        email = data.get('email')
        address=data.get('address', '')
        name=data.get('name')
        add_to_mailing = data.get('mailing', False)

        response, response_status = mautic_api.getContactByEmail(email)
        if response_status == 200:
            contacts = response['contacts']
        else:
            # something went wrong with mautic, return
            return Response({'msg': response}, status=response_status)
        mautic_id = None
        if contacts:
            # subscriber exists on mautic
            mautic_id = list(contacts.keys())[0]
            subscriber =Subscriber.objects.get(mautic_id=mautic_id)
            subscriber.name = name
            subscriber.address = address
            subscriber.save()
        else:
            # subscriber does not exist on mautic
            subscriber = Subscriber.objects.create(name=name, address=address)
            subscriber.save()
            response, response_status = subscriber.save_to_mautic(email)
            if response_status != 200:
                # something went wrong with saving to mautic, abort
                return Response({'msg': response}, status=response_status)
            mautic_id = subscriber.mautic_id

        if add_to_mailing:
            segment_id = settings.SEGMENTS.get('general', None)
            response, response_status = mautic_api.addContactToASegment(segment_id, mautic_id)


        delivery_method = data['delivery_method']
        order = Order.objects.filter(basket=basket)
        if order:
            order.update(
                delivery_method=delivery_method,
                address=data.get('address', ''),
                name=data.get('name'),
                phone=data.get('phone', None),
                email=data.get('email'),
                info=data.get('info', ''))
            order=order[0]
        else:
            order = Order(
                address=data.get('address', ''),
                name=data.get('name'),
                delivery_method=delivery_method,
                basket=basket,
                phone=data.get('phone', None),
                email=data.get('email'),
                payment_id='',
                info=data.get('info', ''))
            order.save()

        return Response(payment.client_token())


class Pay(APIView):
    def post(self, request, format=None):
        basket = get_basket(request)
        order = get_object_or_404(Order, basket=basket)
        data = json.loads(request.body.decode('utf-8'))
        payment_type = data.get('payment_type')
        order.payment_method=payment_type
        order.save()
        url = "https://podpri.djnd.si/admin/shop/order/" + str(order.id) + "/change/"
        if payment_type == 'braintree':
            nonce = data.get('nonce', None)
            pay_response = payment.pay_bt_3d(nonce, order.basket.total, description='Shop')
            if pay_response.is_success:
                order.is_payed=True
                order.transaction_id = pay_response.transaction.id
                order.save()
                msg = order.name + " je nekaj naročil/-a in plačal/-a s kartico: \n"
            else:
                return JsonResponse({'msg': 'failed',
                                     'error': [error.message for error in pay_response.errors.deep_errors]},
                                    status=400)

        elif payment_type == 'upn':
            reference = prepare_upn_data(order)
            msg = order.name + " je nekaj naročil/-a in plačal/-a bo s položnico: \n"

            data = {"id": order.id,
                    "upn_id": signing.dumps(order.id),
                    "date": datetime.now().strftime('%d.%m.%Y'),
                    "price": order.basket.total,
                    "reference": reference,
                    "code": "?",
                    "name": order.name,
                    "address1": order.address,
                    "address2": "",
                    "status": "prepared"}

            if order.is_donation():
                data['code'] = "ADCS"
                data['purpose'] = "Donacija"
            else:
                data['code'] = "GDSV"
                data['purpose'] = "Položnica za naročilo št. " + str(order.id)

            total = order.basket.total
            reference = order.payment_id
            iban = settings.IBAN.replace(' ', '')
            to_name = settings.TO_NAME.strip()
            to_address1 = settings.TO_ADDRESS1.strip()
            to_address2 = settings.TO_ADDRESS2.strip()

            html = get_template('email_poloznica.html')
            context = { 'total': total,
                        'reference': reference,
                        'iban': iban,
                        'to_address1': to_address1,
                        'to_address2': to_address2,
                        'code': data['code'],
                        'purpose': data['purpose'],
                        'bic': 'HDELSI22'}
            html_content = html.render(context)

            pdf = getPDFodOrder(None, signing.dumps(order.id)).render().content

            response, response_status = mautic_api.saveFile('upn.pdf', pdf)
            print(response)
            response, response_status = mautic_api.saveAsset('upn', response['file']['name'])
            print(response)
            asset_id = response['asset']['id']

            #response_contact, response_status = mautic_api.createContact(order.email, order.name, '')
            response_contact, response_status = mautic_api.getContactByEmail(order.email)
            contacts = response_contact['contacts']
            mautic_id = list(contacts.keys())[0]

            # response_mail, response_status = mautic_api.createEmail(
            #     'upn-' + order.email,
            #     '',
            #     'Položnica za tvoj nakup <3',
            #     html_content,
            #     'To je mail za kupca ki, bo/je plačal s položnico',
            #     assetAttachments=[asset_id]
            # )
            email_id = settings.MAIL_TEMPLATES['SHOP_UPN']
            response, response_status = mautic_api.getEmail(email_id)
            content = response["email"]["customHtml"]
            subject = response["email"]["subject"]
            response_mail, response_status = mautic_api.createEmail(
                subject + ' copy-upn-shop ' + to_name,
                subject,
                subject,
                customHtml=content,
                #emailType='list',
                description='',
                assetAttachments=[asset_id],
                template='cards',
                #lists=[1],
                fromAddress=response["email"]["fromAddress"],
                fromName=response["email"]["fromName"]
            )
            mautic_api.sendEmail(
                response_mail['email']['id'],
                mautic_id,
                {}
            )

        for item in basket.items.all():
            msg += " * " + str(item.quantity) + "X " + item.article.name + "\n"
            msg += "Preveri naročilo: " + url
            if order.info:
                msg += '\n Posvetilo: ' + order.info

            send_slack_msg(msg, '#djnd-bot')

        return JsonResponse({'msg': 'prepared'})


@csrf_exempt
def checkout(request):
    if request.method == 'POST':
        basket = get_basket(request)
        if not basket.items.all():
            return JsonResponse({'status': 'error',
                                 'msg': 'Your basket is empty'})
        basket.is_open = False
        basket.save()
        data = get_basket_data(basket)
        data = json.loads(request.body.decode('utf-8'))
        delivery_method = data['delivery_method']

        order = Order.objects.filter(basket=basket)
        if order:
            order.update(delivery_method=delivery_method,
                         address=data.get('address', ''),
                         name=data['name'],
                         phone=data['phone'],
                         email=data['email'],
                         info=data.get('info', ''))
            order=order[0]
        else:
            order = Order(address=data['address'],
                          name=data['name'],
                          delivery_method=delivery_method,
                          basket=basket,
                          phone=data['phone'],
                          email=data['email'],
                          payment_id='',
                          info=data.get('info', ''))
            order.save()

        if payment_type == 'braintree':
            nonce = request.POST.get('nonce', None)

            is_ok, log = payment.pay_bt_3d(nonce, order.basket.total, description='Shop')
            if is_ok:
                order.is_payed=True
                order.save()
                url = "https://podpri.djnd.si/admin/shop/order/" + str(order.id) + "/change/"
                msg = order.name + " je nekaj naročil/-a in plačal/-a je s paypalom: \n"
                for item in order.basket.items.all():
                    msg += " * " + str(item.quantity) + "X " + item.article.name + "\n"
                msg += "Preveri naročilo: " + url
                if order.info:
                    msg += '\n Posvetilo: ' + order.info
                send_slack_msg(msg, '#djnd-bot')

                # update artickles stock
                update_stock(order)
                print("Payment execute successfully")

                return JsonResponse({'msg': 'prepared'})
            else:
                return JsonResponse({'msg': 'failed',
                                     'error': log})

        elif payment_type == 'upn':
            reference = upn(order)
            url = "https://podpri.djnd.si/admin/shop/order/" + str(order.id) + "/change/"
            msg = order.name + " je nekaj naročil/-a in plačal/-a bo s položnico: \n"
            for item in basket.items.all():
                msg += " * " + str(item.quantity) + "X " + item.article.name + "\n"
            msg += "Preveri naročilo: " + url
            if order.info:
                msg += '\n Posvetilo: ' + order.info
            send_slack_msg(msg, '#djnd-bot')

            data = {"id": order.id,
                    "upn_id": signing.dumps(order.id),
                    "date": datetime.now().strftime('%d.%m.%Y'),
                    "price": order.basket.total,
                    "reference": reference,
                    "code": "?",
                    "name": order.name,
                    "address1": order.address,
                    "address2": "",
                    "status": "prepared"}

            if order.is_donation():
                data['code'] = "ADCS"
                data['purpose'] = "Donacija"
            else:
                data['code'] = "GDSV"
                data['purpose'] = "Položnica za naročilo št. " + str(order.id)

            total = order.basket.total
            reference = order.payment_id
            iban = settings.IBAN.replace(' ', '')
            to_name = settings.TO_NAME.strip()
            to_address1 = settings.TO_ADDRESS1.strip()
            to_address2 = settings.TO_ADDRESS2.strip()

            html = get_template('email_poloznica.html')
            context = { 'total': total,
                        'reference': reference,
                        'iban': iban,
                        'to_address1': to_address1,
                        'to_address2': to_address2,
                        'code': data['code'],
                        'purpose': data['purpose'],
                        'bic': 'HDELSI22'}
            html_content = html.render(context)

            pdf = getPDFodOrder(None, signing.dumps(order.id)).render().content

            subject, to = 'Položnica za tvoj nakup <3', order.email
            text_content = strip_tags(html_content)

            send_mail_spam(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                to_mail=to,
                file=(
                    'racun.pdf',
                    pdf,
                    'application/pdf'
                )
            )
            return JsonResponse(data)
        else:
            return JsonResponse({'msg': 'this payment not defined'})
    else:
        return JsonResponse({"msg": "Method \"GET\" not allowed"})


def clear_session(request):
    del request.session['order_key']
    return JsonResponse({'msg': 'clean'})


def get_items_for_basket(request):
    html_from_view = ItemView.get(ItemView, request=request).data
    count =  sum([item['quantity'] for item in html_from_view])
    return html_from_view, count
