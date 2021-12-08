from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import status, views, permissions, mixins, viewsets
from rest_framework.response import Response

from djnd_supporters import models, mautic_api, authentication, serializers
from djndonacije import payment

from datetime import datetime

import slack
import requests

from djnd_supporters.views import getPDForDonation
from django.template.loader import get_template
from django.core import signing

sc = slack.WebClient(settings.SLACK_KEY, timeout=30)


class UsersImport(views.APIView):
    """
    This endpoint just for import users
    """
    def post(self, request, format=None):
        data = request.data
        email = data.get('email', None)
        lists = data.get('lists', None)
        if email:
            subscriber = models.Subscriber.objects.create()
            subscriber.save()
            subscriber.save_to_mautic(email, send_email=False)

            contact_id = subscriber.mautic_id
            reponses = []
            for segment in lists:
                segment_id = settings.SEGMENTS.get(segment, None)
                if segment_id:
                    response, resp_status =  mautic_api.addContactToASegment(segment_id, contact_id)
                    reponses.append(response)

            return Response({"contact added": True})
        return Response({"email missing": True})


class GetOrAddSubscriber(views.APIView):
    def get_subscriber_id(self, email, send_email=False):
        mautic_id = None
        response, response_status = mautic_api.getContactByEmail(email)
        if response_status == 200:
            contacts = response['contacts']
            if contacts:
                mautic_id = list(contacts.keys())[0]
            else:
                subscriber = models.Subscriber.objects.create()
                subscriber.save()
                response, response_status = subscriber.save_to_mautic(email, send_email)
                if response_status != 200:
                    return Response({'msg': response}, status=response_status)
                else:
                    mautic_id = subscriber.mautic_id
        return mautic_id

class Subscribe(views.APIView):
    """
    Add subscriber od edit subscriptions
    POST:
        email
        segment
    """
    def post(self, request, format=None):
        data = request.data
        email = data.get('email', None)
        segment = data.get('segment', None)
        if email:
            response, response_status = mautic_api.getContactByEmail(email)
            if response_status == 200:
                contacts = response['contacts']
                if contacts:
                    mautic_id = list(contacts.keys())[0]
                    if segment:
                        mautic_api.addContactToASegment(segment, mautic_id)
                    edit_subscriptopn_template = settings.EDIT_SUBSCRIPTIPNS_TEMPLATES.get(segment, settings.MAIL_TEMPLATES['EDIT_SUBSCRIPTIPNS'])
                    response, response_status = mautic_api.sendEmail(
                        edit_subscriptopn_template,
                        mautic_id,
                        {
                        }
                    )
                    return Response({'msg': 'mail sent'})
                else:
                    subscriber = models.Subscriber.objects.create()
                    subscriber.save()
                    response, response_status = subscriber.save_to_mautic(email)
                    if response_status != 200:
                        return Response({'msg': response}, status=response_status)
                    else:
                        if segment:
                            mautic_api.addContactToASegment(segment, subscriber.mautic_id)
                        response, response_status = mautic_api.sendEmail(
                            settings.MAIL_TEMPLATES['WELLCOME_MAIL'],
                            subscriber.mautic_id,
                            {}
                        )
                        return Response({'msg': 'mail sent'})
            else:
                return Response({'msg': response}, status=response_status)
        return Response({'error': 'Missing email and/or token.'}, status=status.HTTP_409_CONFLICT)


class ManageSegments(views.APIView):
    """
    POST/DELETE

    /campaigns/<campaign>/contact/<token>
    campaign: name of campaign
    token: user token
    """
    authentication_classes = [authentication.SubscriberAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, segment, format=None):
        contact_id = request.user.mautic_id
        segment_id = settings.SEGMENTS.get(segment, None)
        if not segment_id:
            return Response({'msg': 'Segment doesnt exist'}, status=status.HTTP_404_NOT_FOUND)

        if contact_id:
            response, response_status = mautic_api.addContactToASegment(segment_id, contact_id)
            if response_status == 200:
                return Response(response)
            else:
                return Response(response, status=response_status)
        else:
            return Response({'msg': 'Subscriber doesnt exist'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, segment, format=None):
        contact_id = request.user.mautic_id
        segment_id = settings.SEGMENTS.get(segment, None)
        if not segment_id:
            return Response({'msg': 'Segment doesnt exist'}, status=status.HTTP_404_NOT_FOUND)

        if contact_id:
            response, response_status = mautic_api.removeContactFromASegment(segment_id, contact_id)
            if response_status == 200:
                return Response(response)
            else:
                return Response({'msg': response}, status=response_status)
        else:
            return Response({'msg': 'Subscriber doesnt exist'}, status=status.HTTP_404_NOT_FOUND)


class Segments(views.APIView):
    authentication_classes = [authentication.SubscriberAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        response, response_status = mautic_api.getSegments()
        if response_status == 200:
            return Response({'segments': [value for id, value in response['lists'].items()]})
        else:
            return Response({'msg': response}, status=response_status)


class UserSegments(views.APIView):
    authentication_classes = [authentication.SubscriberAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        contact_id = request.user.mautic_id
        response, response_status = mautic_api.getSegmentsOfContact(contact_id)
        if response_status == 200:
            segments = response['lists']
            if segments:
                return Response({'segments': [value for id, value in segments.items()]})
            else:
                return Response({'segments': []})
        else:
            return Response({'msg': response}, status=response_status)


class Donate(views.APIView):
    """
    GET get client token

    POST json data:
     - nonce
     - amount
    """
    authentication_classes = [authentication.SubscriberAuthentication]
    def get(self, request):
        return Response(payment.client_token())

    '''
        CHANGE REQUEST
         - post only nonce and amount process payment with pay_by_3d
         - upon second request post email, name, add_to_mailing, address
    '''

    def post(self, request):
        data = request.data
        nonce = data.get('nonce', None)
        amount = data.get('amount', None)
        email = data.get('email', None)
        name = data.get('name', '')
        add_to_mailing = data.get('mailing', False)
        address = data.get('address', '')
        payment_type = data.get('payment_type', 'braintree')

        # if nonce not present deny
        #if not nonce:
        #    return Response({'msg': 'Missing nonce.'}, status=status.HTTP_400_BAD_REQUEST)

        # if no amount deny
        if not amount:
            return Response({'msg': 'Missing amount.'}, status=status.HTTP_400_BAD_REQUEST)

        # email and nonce are both present
        response, response_status = mautic_api.getContactByEmail(email)
        if response_status == 200:
            contacts = response['contacts']
        else:
            # something went wrong with mautic, return
            return Response({'msg': response}, status=response_status)
        print(contacts)
        mautic_id = None
        if contacts:
            # subscriber exists on mautic
            mautic_id = list(contacts.keys())[0]
            subscriber = models.Subscriber.objects.get(mautic_id=mautic_id)
            subscriber.name = name
            subscriber.address = address
            subscriber.save()
        else:
            # subscriber does not exist on mautic
            subscriber = models.Subscriber.objects.create(name=name, address=address)
            subscriber.save()
            response, response_status = subscriber.save_to_mautic(email, send_email=False)
            if response_status != 200:
                # something went wrong with saving to mautic, abort
                return Response({'msg': response}, status=response_status)
            mautic_id = subscriber.mautic_id

        # add to mailing if they agreed
        if add_to_mailing:
            segment_id = settings.SEGMENTS.get('general', None)
            response, response_status = mautic_api.addContactToASegment(segment_id, mautic_id)

        segment_id = settings.SEGMENTS.get('donations', None)
        response, response_status = mautic_api.addContactToASegment(segment_id, mautic_id)

        if payment_type == 'upn':
            # TODO UPN
            donation = models.Donation(
                amount=amount,
                nonce=nonce,
                subscriber=subscriber,
                is_paid=False,
                payment_method='upn')
            donation.save()
            reference = 'SI00 11' + str(donation.id).zfill(8)
            donation.reference = reference
            donation.save()
            image = models.Image(donation=donation)
            image.save()

            data = {"id": donation.id,
                    "upn_id": signing.dumps(donation.id),
                    "date": datetime.now().strftime('%d.%m.%Y'),
                    "price": amount,
                    "reference": reference,
                    "code": "?",
                    "name": name,
                    "address1": address,
                    "address2": "",
                    "status": "prepared"}

            data['code'] = "ADCS"
            data['purpose'] = "Donacija"

            total = amount
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

            pdf = getPDForDonation(None, donation.id).render().content

            response, response_status = mautic_api.saveFile('upn.pdf', pdf)
            print(response)
            response, response_status = mautic_api.saveAsset('upn', response['file']['name'])
            print(response)
            asset_id = response['asset']['id']

            email_id = settings.MAIL_TEMPLATES['DONATION_WITHOUT_GIFT_UPN'] if donation.amount < 24 else settings.MAIL_TEMPLATES['DONATION_WITH_GIFT_UPN']
            response, response_status = mautic_api.getEmail(email_id)
            content = response["email"]["customHtml"]
            subject = response["email"]["subject"]
            response_mail, response_status = mautic_api.createEmail(
                subject + ' copy-for ' + name,
                subject,
                subject,
                customHtml=content,
                #emailType='list',
                description='email for donation with UPN',
                assetAttachments=[asset_id],
                template='cards',
                #lists=[1],
                fromAddress=response["email"]["fromAddress"],
                fromName=response["email"]["fromName"]
            )

            #response_mail, response_status = mautic_api.createEmail(
            #     'upn-' + order.email,
            #     '',
            #     'Položnica za tvoj nakup <3',
            #     html_content,
            #     'To je mail za kupca ki, bo/je plačal s položnico',
            #     assetAttachments=[asset_id]
            # )
            # mautic_api.sendEmail(
            #     response_mail['email']['id'],
            #     mautic_id,
            #     {}
            # )
            mautic_api.sendEmail(
                response_mail['email']['id'],
                mautic_id,
                {
                    'tokens': {
                        'upload_image': donation.image.get_upload_url()
                    }
                })

        elif payment_type == 'braintree':
            result = payment.pay_bt_3d(nonce, float(amount), taxExempt=True, description='DJND donacija')
            if result.is_success:
                # create donation and image object without subscriber
                transaction_id = result.transaction.id
                payment_instrument_type = result.transaction.payment_instrument_type
                if payment_instrument_type == 'paypal_account':
                    payment_method = 'braintree-paypal'
                else:
                    payment_method = 'braintree'
                donation = models.Donation(
                    amount=amount,
                    nonce=nonce,
                    subscriber=subscriber,
                    transaction_id=transaction_id,
                    payment_method=payment_method
                )
                donation.save()
                image = models.Image(donation=donation)
                image.save()
                        # Send email thanks for donation
                if donation.amount < 24:
                    response, response_status = mautic_api.sendEmail(
                        settings.MAIL_TEMPLATES['DONATION_WITHOUT_GIFT'],
                        subscriber.mautic_id,
                        {
                            'tokens': {
                                'upload_image': donation.image.get_upload_url()
                            }
                        }
                    )
                else:
                    response, response_status = mautic_api.sendEmail(
                        settings.MAIL_TEMPLATES['DONATION_WITH_GIFT'],
                        subscriber.mautic_id,
                        {
                            'tokens': {
                                'upload_image': donation.image.get_upload_url()
                            }
                        }
                    )
            else:
                return Response({'msg': result.message}, status=status.HTTP_400_BAD_REQUEST)

        try:
            name = name.split(' ')[0]
        except:
            pass
        try:
            msg = ( name if name else 'Dinozaver' ) + ' nam je podarila donacijo v višini: ' + str(donation.amount)
            sc.api_call(
                "chat.postMessage",
                json={
                    'channel': "#djnd-bot",
                    'text': msg
                }
            )
        except:
            pass

        return Response({
            'msg': 'Thanks <3',
            'upload_token': donation.image.token
        })


class GiftDonate(views.APIView):
    """
    GET get client token

    POST json data:
     - nonce
     - amount
    """
    authentication_classes = [authentication.SubscriberAuthentication]
    def get(self, request):
        return Response({'token' :payment.client_token()})

    '''
        CHANGE REQUEST
        same as Donate post
    '''

    def post(self, request):
        data = request.data
        nonce = data.get('nonce', None)
        gifts_amounts = data.get('gifts_amounts', [])
        email = data.get('email', None)
        amount = data.get('amount', None)
        name = data.get('name', '')
        add_to_mailing = data.get('mailing', False)
        address = data.get('address', '')

        # if nonce not present deny
        if not nonce:
            return Response({'msg': 'Missing nonce.'}, status=status.HTTP_400_BAD_REQUEST)

        # if email not present, try to pay
        if not email:
            # if no amount deny
            if not amount:
                return Response({'msg': 'Missing amount.'}, status=status.HTTP_400_BAD_REQUEST)
            # if no gifts_amounts deny
            if not gifts_amounts:
                return Response({'msg': 'Missing gifts_amounts.'}, status=status.HTTP_400_BAD_REQUEST)

            result = payment.pay_bt_3d(nonce, float(amount), taxExempt=True, description='Gift donate')
            new_subscribers = []
            if result.is_success:
                # create donation and image object without subscriber
                new_gift = models.Gift(amount=amount, nonce=nonce)
                new_gift.save()
                for gift_amount in gifts_amounts:
                    new_subscriber = models.Subscriber.objects.create()
                    new_subscriber.save()
                    donation = models.Donation(
                        amount=gift_amount,
                        subscriber=new_subscriber,
                        is_assigned=False
                    )
                    donation.save()
                    image = models.Image(donation=donation)
                    image.save()
                    new_gift.gifts.add(donation)
                    new_subscribers.append({
                        'subscriber_token': new_subscriber.token,
                        'amount': gift_amount
                    })

                return Response({
                    'msg': 'Thanks <3',
                    'nonce': nonce,
                    'gifts': new_subscribers
                })
            else:
                return Response({'msg': result.message}, status=status.HTTP_400_BAD_REQUEST)

        # email and nonce are both present
        response, response_status = mautic_api.getContactByEmail(email)
        if response_status == 200:
            contacts = response['contacts']
        else:
            # something went wrong with mautic, return
            return Response({'msg': response}, status=response_status)
        print(contacts)
        mautic_id = None
        if contacts:
            # subscriber exists on mautic
            mautic_id = list(contacts.keys())[0]
            subscriber = models.Subscriber.objects.get(mautic_id=mautic_id)
            subscriber.name = name
            subscriber.address = address
            subscriber.save()
        else:
            # subscriber does not exist on mautic
            subscriber = models.Subscriber.objects.create(name=name, address=address)
            subscriber.save()
            response, response_status = subscriber.save_to_mautic(email, send_email=False)
            if response_status != 200:
                # something went wrong with saving to mautic, abort
                return Response({'msg': response}, status=response_status)
            mautic_id = subscriber.mautic_id

        # add to mailing if they agreed
        if add_to_mailing:
            segment_id = settings.SEGMENTS.get('general', None)
            response, response_status = mautic_api.addContactToASegment(segment_id, mautic_id)

        segment_id = settings.SEGMENTS.get('donations', None)
        response, response_status = mautic_api.addContactToASegment(segment_id, mautic_id)

        # finally connect gift to person
        gift = models.Gift.objects.get(nonce=nonce)
        gift.subscriber = subscriber
        gift.save()
        if gift.amount < 11:
            response, response_status = mautic_api.sendEmail(
                settings.MAIL_TEMPLATES['GIFT_WITHOUT_GIFT'],
                mautic_id,
                {}
            )
        else:
            response, response_status = mautic_api.sendEmail(
                settings.MAIL_TEMPLATES['GIFT_WITH_GIFT'],
                mautic_id,
                {}
            )

        try:
            msg = ( name if name else 'Dinozaver' ) + ' nam je podarila donacijo v višini: ' + str(gift.amount)
            sc.api_call(
                "chat.postMessage",
                json={
                    'channel': "#djnd-bot",
                    'text': msg
                }
            )
        except:
            pass

        return Response({
            'msg': 'Thanks <3',
            'owner_token': subscriber.token
        })


class AssignGift(views.APIView):
    def get(self, request, token):
        subscriber = models.Subscriber.objects.get(token=token)
        unassigned_donations = models. Donation.objects.filter(
            gifts__subscriber=subscriber,
            is_assigned=False
        )
        return Response({
            'gifts': [{
                'gift_token': gift.subscriber.token,
                'amount': gift.amount
            }for gift in unassigned_donations]
        })

    def post(self, request):
        data = request.data
        owner_token = data.get('owner_token', None)

        gift_email = data.get('gift_email', None)
        subscriber_token = data.get('subscriber_token')
        name = data.get('name', None)
        message = data.get('message', None)

        subscriber = models.Subscriber.objects.get(token=owner_token)

        new_subscriber = models.Subscriber.objects.get(token=subscriber_token)
        donation = models.Donation.objects.filter(subscriber=new_subscriber)
        if donation:
            donation = donation[0]
            if donation.is_assigned:
                return Response({
                    'msg': 'donation is already assigned',
                    },
                    status=status.HTTP_409_CONFLICT
                )
            mautic_id = None
            response, response_status = mautic_api.getContactByEmail(gift_email)
            if response_status == 200:
                contacts = response['contacts']
            else:
                return Response({'msg': response}, status=response_status)
            if contacts:
                mautic_id = list(contacts.keys())[0]
            else:
                print('dodaj novga')
                new_subscriber.name = name
                new_subscriber.save()
                response, response_status = new_subscriber.save_to_mautic(gift_email, send_email=False)

                if response_status != 200:
                    return Response({'msg': response}, status=response_status)

                mautic_id = new_subscriber.mautic_id

            print(mautic_id)
            message = message.replace('\n', '<br>')
            if name:
                message = name + '!<br><br>' + message
            message = message + '<br>' + subscriber.name + '<br><br>Danes je nov dar! <3'
            response, response_status = mautic_api.sendEmail(
                settings.MAIL_TEMPLATES['CUSTOM_GIFT'],
                mautic_id,
                {
                    'tokens': {
                        'message': message,
                        'sender_name': subscriber.name,
                        'upload_image': donation.image.get_upload_url()
                    }
                }
            )
            if response_status == 200:
                donation.is_assigned = True
                donation.save()
            else:
                return Response({'msg': 'cannot send message, please try again'}, status=status.HTTP_409_CONFLICT)

            if subscriber.gifts.last().gifts.filter(is_assigned=False).count() == 0:
                response, response_status = mautic_api.sendEmail(
                    settings.MAIL_TEMPLATES['GIFT_SENT'],
                    subscriber.mautic_id,
                    {}
                )
                pass

            return Response({
                'msg': 'Gift was sent',
            })
        return Response({
                'msg': 'donation was not found',
            },
            status=status.HTTP_409_CONFLICT
        )


class DonationsStats(views.APIView):
    def get(self, request):
        return Response({
            'donations': models.Donation.objects.filter(created__gte=datetime(day=1, month=12, year=2020)).count(),
            'collected': sum(models.Donation.objects.filter(created__gte=datetime(day=1, month=12, year=2020).values_list('amount', flat=True))),
            'max-donation': max(models.Donation.objects.filter(created__gte=datetime(day=1, month=12, year=2020).values_list('amount', flat=True)))
        })


class ImageViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    lookup_field = 'token'
    queryset = models.Image.objects.filter(created__gte=datetime(day=1, month=12, year=2020))
    serializer_class = serializers.ImageSerializer


class AgrumentMailApiView(views.APIView):
    def post(self, request):
        data = request.data
        if settings.AGRUM_TOKEN != request.META.get('HTTP_AUTHORIZATION', None):
            return Response({
                    'msg': 'You have no permissions for do that.'
                }, status=403)
        short_url_response = requests.get('https://djnd.si/yomamasofat/?fatmama=%s' % data['url'])
        if short_url_response:

            email_id = int(data.get('email_template_id', 42))

            # get tempalte of email
            response, response_status = mautic_api.getEmail(email_id)

            # make changes in email
            content = response["email"]["customHtml"]
            content = content.replace('{content}', data['content_html'])
            content = content.replace('{image}', data['image_url'])
            content = content.replace('{short_url}', short_url_response.text)

            content = content.replace('{source_name}', data.get('image_source', ''))
            content = content.replace('{source_url}', data.get('image_source_url', ''))

            # create new email
            response, response_status = mautic_api.createEmail(
                "Agrument: " + data['title'],
                data['title'],
                data['title'],
                customHtml=content,
                emailType='list',
                description="Agrument",
                assetAttachments=None,
                template='cards',
                lists=[1],
                fromAddress='agrument@posta.danesjenovdan.si',
                fromName='Agrument'
            )
            if response_status == 200:
                new_email_id = response['email']['id']

                if response_status == 200:
                    #print(mautic_api.sendEmail(42, 315, {
                    #    'tokens': {
                    #        "content": data['content_html'],
                    #        "image": data['image_url'],
                    #        "short_url": short_url_response.text
                    #    }
                    #}))
                    print(
                        mautic_api.sendEmailToSegment(
                            new_email_id, {}
                        )
                    )
                else:
                    return Response({
                        'msg': 'cannot send email'
                        },
                        status=409
                    )
            else:
                return Response({
                    'msg': 'cannot send email'
                    },
                    status=409
                )
        return Response({
            'msg': 'sent'
        })


class RecurringDonate(views.APIView):
    authentication_classes = [authentication.SubscriberAuthentication]
    def get(self, request):
        return Response({})

    def post(self, request):
        data = request.data
        nonce = data.get('nonce', None)
        amount = data.get('amount', None)
        email = data.get('email', None)
        name = data.get('name', '')
        add_to_mailing = data.get('mailing', False)
        address = data.get('address', '')
        customer_id = data.get('customer_id', '')

        # if nonce not present deny
        if not nonce:
            return Response({'msg': 'Missing nonce.'}, status=status.HTTP_400_BAD_REQUEST)

        # if email not present, try to pay
        if not email:
            # if no amount deny
            if not amount:
                return Response({'msg': 'Missing amount.'}, status=status.HTTP_400_BAD_REQUEST)

            result = payment.create_subscription(nonce, customer_id, float(amount))
            if result.is_success:
                # create donation without subscriber
                subscriber = models.Subscriber.objects.get(nonce=nonce)
                donation = models.RecurringDonation(
                    amount=amount,
                    subscriber=subscriber,
                    subscription_id=result.subscription.id
                )
                donation.save()
                image = models.Image(donation=donation)
                image.save()

                return Response({
                    'msg': 'Thanks <3',
                    'nonce': nonce,
                    'upload_token': image.token
                })
            else:
                return Response({'msg': result.message}, status=status.HTTP_400_BAD_REQUEST)

        # email and nonce are both present
        response, response_status = mautic_api.getContactByEmail(email)
        if response_status == 200:
            contacts = response['contacts']
        else:
            # something went wrong with mautic, return
            return Response({'msg': response}, status=response_status)
        mautic_id = None
        subscriber = None
        if contacts:
            # subscriber exists on mautic
            mautic_id = list(contacts.keys())[0]
            try:
                subscriber = models.Subscriber.objects.get(mautic_id=mautic_id)
            except:
                subscriber = models.Subscriber.objects.create(
                    mautic_id=mautic_id
                )
                subscriber.save()
            subscriber.name = name
            subscriber.address = address
            subscriber.save()
        else:
            # subscriber does not exist on mautic
            subscriber = models.Subscriber.objects.create(
                name=name,
                address=address,
            )
            subscriber.save()
            response, response_status = subscriber.save_to_mautic(email, send_email=False)
            if response_status != 200:
                # something went wrong with saving to mautic, abort
                return Response({'msg': response}, status=response_status)
            mautic_id = subscriber.mautic_id

        # add to mailing if they agreed
        if add_to_mailing:
            segment_id = settings.SEGMENTS.get('general', None)
            response, response_status = mautic_api.addContactToASegment(segment_id, mautic_id)

        segment_id = settings.SEGMENTS.get('donations', None)
        response, response_status = mautic_api.addContactToASegment(segment_id, mautic_id)

        result = payment.create_subscription(nonce, customer_id, float(amount))
        if result.is_success:
            # create donation without subscriber
            donation = models.RecurringDonation(
                amount=amount,
                subscriber=subscriber,
                subscription_id=result.subscription.id
            )
            donation.save()
            image = models.Image(donation=donation)
            image.save()
        else:
            return Response({'msg': result.message}, status=status.HTTP_400_BAD_REQUEST)


        if donation.amount < 24:
            response, response_status = mautic_api.sendEmail(
                settings.MAIL_TEMPLATES['DONATION_WITHOUT_GIFT'],
                subscriber.mautic_id,
                {
                    'tokens': {
                        'upload_image': donation.image.get_upload_url()
                    }
                }
            )
        else:
            response, response_status = mautic_api.sendEmail(
                settings.MAIL_TEMPLATES['DONATION_WITH_GIFT'],
                subscriber.mautic_id,
                {
                    'tokens': {
                        'upload_image': donation.image.get_upload_url()
                    }
                }
            )

        # Send email thanks for donation
        # response, response_status = mautic_api.sendEmail(
        #     settings.MAIL_TEMPLATES['DONATION_WITHOUT_GIFT'],
        #     subscriber.mautic_id,
        #     {}
        # )
        try:
            name = name.split(' ')[0]
        except:
            pass
        try:
            msg = ( name if name else 'Dinozaverka' ) + ' nam je podarila mesečno donacijo v višini: ' + str(donation.amount)
            sc.api_call(
                "chat.postMessage",
                json={
                    'channel': "#djnd-bot",
                    'text': msg
                }
            )
        except:
            pass

        return Response({
            'msg': 'Thanks <3',
            'upload_token': image.token
        })

    def update(self, request):
        return Response({})


class DonationCampaignStatistics(views.APIView):
    """
    GET get statistics of campaign
    """
    authentication_classes = [authentication.SubscriberAuthentication]
    def get(self, request, campaign_id=0):
        donation_campaign = get_object_or_404(models.DonationCampaign, pk=campaign_id)
        donations = donation_campaign.donations.filter(is_paid=True)
        return Response({
            'donation-amount': sum([d.get_amount() for d in donations]),
            'donation-count': donations.count()
        })


class GenericDonationCampaign(views.APIView):
    """
    GET get client token and donation specifics

    POST json data:
     - nonce
     - amount
     - email
     - name
     - mailing
     - address
     - payment_type
    """
    authentication_classes = [authentication.SubscriberAuthentication]
    def get(self, request, campaign_id=0):
        # TODO return specifications of donation campaign
        print(campaign_id)
        donation_campaign = get_object_or_404(models.DonationCampaign, pk=campaign_id)
        donation_obj = serializers.DonationCampaignSerializer(donation_campaign).data
        donation_obj.update(payment.client_token())
        return Response(donation_obj)


    def post(self, request, campaign_id=0):
        data = request.data
        nonce = data.get('nonce', None)
        amount = data.get('amount', None)
        email = data.get('email', None)
        name = data.get('name', '')
        add_to_mailing = data.get('mailing', False)
        address = data.get('address', '')
        payment_type = data.get('payment_type', 'braintree')

        donation_campaign = get_object_or_404(models.DonationCampaign, pk=campaign_id)

        # if no amount deny
        if not amount:
            return Response({'msg': 'Missing amount.'}, status=status.HTTP_400_BAD_REQUEST)

        # email and nonce are both present
        response, response_status = mautic_api.getContactByEmail(email)
        if response_status == 200:
            contacts = response['contacts']
        else:
            # something went wrong with mautic, return
            return Response({'msg': response}, status=response_status)
        print(contacts)
        mautic_id = None
        if contacts:
            # subscriber exists on mautic
            mautic_id = list(contacts.keys())[0]
            subscriber = models.Subscriber.objects.get(mautic_id=mautic_id)
            subscriber.name = name
            subscriber.address = address
            subscriber.save()
        else:
            # subscriber does not exist on mautic
            subscriber = models.Subscriber.objects.create(name=name, address=address)
            subscriber.save()
            response, response_status = subscriber.save_to_mautic(email, send_email=False)
            if response_status != 200:
                # something went wrong with saving to mautic, abort
                return Response({'msg': response}, status=response_status)
            mautic_id = subscriber.mautic_id

        # add to mailing if they agreed
        if add_to_mailing and donation_campaign.add_to_mailing:
            response, response_status = mautic_api.addContactToASegment(donation_campaign.add_to_mailing, mautic_id)


        if payment_type == 'upn':
            # check if campaign supports upn payments
            if not donation_campaign.has_upn:
                return Response({'msg': 'This campaign does not support UPN payments.'}, status=status.HTTP_400_BAD_REQUEST)
            donation = models.Donation(
                amount=amount,
                nonce=nonce,
                subscriber=subscriber,
                is_paid=False,
                payment_method='upn',
                campaign=donation_campaign)
            donation.save()
            reference = 'SI00 11' + str(donation.id).zfill(8)
            donation.reference = reference
            donation.save()

            pdf = getPDForDonation(None, donation.id).render().content

            response, response_status = mautic_api.saveFile('upn.pdf', pdf)
            response, response_status = mautic_api.saveAsset('upn', response['file']['name'])
            asset_id = response['asset']['id']

            email_id = donation_campaign.upn_email_template

            response, response_status = mautic_api.getEmail(email_id)
            content = response["email"]["customHtml"]
            subject = response["email"]["subject"]
            response_mail, response_status = mautic_api.createEmail(
                subject + ' copy-for ' + name,
                subject,
                subject,
                customHtml=content,
                #emailType='list',
                description='email for donation with UPN',
                assetAttachments=[asset_id],
                template='cards',
                #lists=[1],
                fromAddress=response["email"]["fromAddress"],
                fromName=response["email"]["fromName"]
            )


            mautic_api.sendEmail(
                response_mail['email']['id'],
                mautic_id,
                {})


        elif payment_type == 'braintree':
            # check if campaign supports braintree payments
            if not donation_campaign.has_braintree:
                return Response({'msg': 'This campaign does not support braintree payments.'}, status=status.HTTP_400_BAD_REQUEST)

            result = payment.pay_bt_3d(
                nonce,
                float(amount),
                taxExempt=True,
                description=donation_campaign.name,
                campaign=donation_campaign.name,
            )
            if result.is_success:
                transaction_id = result.transaction.id
                payment_instrument_type = result.transaction.payment_instrument_type
                if payment_instrument_type == 'paypal_account':
                    payment_method = 'braintree-paypal'
                else:
                    payment_method = 'braintree'
                # create donation and image object without subscriber
                donation = models.Donation(
                    amount=amount,
                    nonce=nonce,
                    subscriber=subscriber,
                    campaign=donation_campaign,
                    transaction_id=transaction_id,
                    payment_method=payment_method)
                donation.save()

                # send email if tempalte is setted in donation campaign
                if donation_campaign.bt_email_template:
                    response, response_status = mautic_api.sendEmail(
                        donation_campaign.bt_email_template,
                        subscriber.mautic_id,
                        {}
                    )
            else:
                return Response({'msg': result.message}, status=status.HTTP_400_BAD_REQUEST)


        # send slack msg
        try:
            name = name.split(' ')[0]
        except:
            pass
        try:
            msg = ( name if name else 'Dinozaverka' ) + ' nam je podarila donacijo za [ ' + donation_campaign.name + ' ] v višini: ' + str(donation.amount)
            sc.api_call(
                "chat.postMessage",
                json={
                    'channel': "#djnd-bot",
                    'text': msg
                }
            )
        except:
            pass

        response = {
            'msg': 'Thanks <3',
        }
        if donation_campaign.has_upload_image:
            image = models.Image(donation=donation)
            image.save()
            response.update({
                'upload_token': image.token
            })


        return Response(response)

class GenericSubscribableDonationCampaign(views.APIView):
    """
    GET get client token

    POST json data:
     - nonce
     - amount
    """
    authentication_classes = [authentication.SubscriberAuthentication]
    def post(self, request, campaign_id=0):
        data = request.data
        nonce = data.get('nonce', None)
        amount = data.get('amount', None)
        email = data.get('email', None)
        name = data.get('name', '')
        add_to_mailing = data.get('mailing', False)
        address = data.get('address', '')
        payment_type = data.get('payment_type', 'braintree')
        customer_id = data.get('customer_id', '')

        donation_campaign = get_object_or_404(models.DonationCampaign, pk=campaign_id)

        # if no amount deny
        if not amount:
            return Response({'msg': 'Missing amount.'}, status=status.HTTP_400_BAD_REQUEST)

        response, response_status = mautic_api.getContactByEmail(email)
        if response_status == 200:
            contacts = response['contacts']
        else:
            # something went wrong with mautic, return
            return Response({'msg': response}, status=response_status)
        print(contacts)
        mautic_id = None
        if contacts:
            # subscriber exists on mautic
            mautic_id = list(contacts.keys())[0]
            subscriber = models.Subscriber.objects.get(mautic_id=mautic_id)
            subscriber.name = name
            subscriber.address = address
            subscriber.save()
        else:
            # subscriber does not exist on mautic
            subscriber = models.Subscriber.objects.create(name=name, address=address)
            subscriber.save()
            response, response_status = subscriber.save_to_mautic(email, send_email=False)
            if response_status != 200:
                # something went wrong with saving to mautic, abort
                return Response({'msg': response}, status=response_status)
            mautic_id = subscriber.mautic_id

        # add to mailing if they agreed
        if add_to_mailing and donation_campaign.add_to_mailing:
            response, response_status = mautic_api.addContactToASegment(donation_campaign.add_to_mailing, mautic_id)

        # check if campaign supports braintree payments
        if not donation_campaign.has_braintree_subscription:
            return Response({'msg': 'This campaign does not support braintree payments.'}, status=status.HTTP_400_BAD_REQUEST)

        result = payment.create_subscription(nonce, customer_id, float(amount))
        if result.is_success:
            # create donation without subscriber
            donation = models.RecurringDonation(
                amount=amount,
                subscriber=subscriber,
                subscription_id=result.subscription.id,
                campaign=donation_campaign,
            )
            donation.save()
            if donation_campaign.bt_subscription_email_template:
                response, response_status = mautic_api.sendEmail(
                    donation_campaign.bt_subscription_email_template,
                    subscriber.mautic_id,
                    {}
                )
        else:
            return Response({'msg': result.message}, status=status.HTTP_400_BAD_REQUEST)


        # send slack msg
        try:
            name = name.split(' ')[0]
        except:
            pass
        try:
            msg = ( name if name else 'Dinozaverka' ) + ' nam je podarila mesecno donacijo za ' + donation_campaign.name + ' v višini: ' + str(donation.amount)
            sc.api_call(
                "chat.postMessage",
                json={
                    'channel': "#djnd-bot",
                    'text': msg
                }
            )
        except:
            pass

        return Response({
            'msg': 'Thanks <3',
        })


class SendEmailApiView(GetOrAddSubscriber):
    """
    POST json data:
     - email
     - email_template_id

    Authorization:
        athorization token
    """
    def post(self, request, campaign_id=0):
        data = request.data
        email = data.get('email', None)
        email_template_id = data.get('email_template_id', None)
        token = request.META.get('HTTP_AUTHORIZATION')
        if token not in [settings.EMAIL_TOKEN, settings.AGRUM_TOKEN]:
            return Response({'msg': 'You dont have permissions for send emails'}, status=403)
        if not email or not email_template_id:
            return Response({'msg': 'Try again'}, status=status.HTTP_400_BAD_REQUEST)
        user_mautic_id = self.get_subscriber_id(email)
        mautic_api.sendEmail(email_template_id, user_mautic_id, {})
        return Response({'msg': 'mail sent'})


class CreateAndSendMailApiView(views.APIView):
    def post(self, request):
        data = request.data
        print(data)
        if settings.AGRUM_TOKEN != request.META.get('HTTP_AUTHORIZATION', None):
            return Response({
                    'msg': 'You have no permissions for do that.'
                }, status=403)

        email_data = {
            'name': data['title'],
            'title': data['title'],
            'subject': data['title'],
            'customHtml': data['content'],
            'emailType': 'list',
            'description': data["description"],
            'assetAttachments': None,
            'template': 'cards',
            'lists': data['segments'],
        }

        if 'fromName' in data.keys():
            email_data.update(fromName=data['fromName'])

        if 'fromAddress' in data.keys():
            email_data.update(fromAddress=data['fromAddress'])

        # create new email
        response, response_status = mautic_api.createEmail(**email_data)
        if response_status == 200:
            new_email_id = response['email']['id']

            if response_status == 200:
                #print(mautic_api.sendEmail(42, 315, {
                #    'tokens': {
                #        "content": data['content_html'],
                #        "image": data['image_url'],
                #        "short_url": short_url_response.text
                #    }
                #}))
                print(
                    mautic_api.sendEmailToSegment(
                        new_email_id, {}
                    )
                )
            else:
                return Response({
                    'msg': 'cannot send email'
                    },
                    status=409
                )
        else:
            return Response({
                'msg': response
                },
                status=409
            )
        return Response({
            'msg': 'sent'
        })
