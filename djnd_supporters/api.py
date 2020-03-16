from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import status, views, permissions, mixins, viewsets
from rest_framework.response import Response

from djnd_supporters import models, mautic_api, authentication, serializers
from djndonacije import payment
from shop.qrcode import generate_upn_qr

from decimal import Decimal

import slack

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

class Subscribe(views.APIView):
    """
    This endpoint is for make braintree subscription
    """
    def post(self, request, format=None):
        data = request.data
        email = data.get('email', None)
        if email:
            response, response_status = mautic_api.getContactByEmail(email)
            if response_status == 200:
                contacts = response['contacts']
                if contacts:
                    mautic_id = list(contacts.keys())[0]
                    response, response_status = mautic_api.sendEmail(
                        settings.MAIL_TEMPLATES['EDIT_SUBSCRIPTIPNS'],
                        mautic_id,
                        {}
                    )
                    return Response({'msg': 'mail sent'})
                else:
                    subscriber = models.Subscriber.objects.create()
                    subscriber.save()
                    response, response_status = subscriber.save_to_mautic(email)
                    if response_status != 200:
                        return Response({'msg': response}, status=response_status)
                    else:
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


class DonateUPN(views.APIView):
    def post(self, request):
        data = request.data
        nonce = data.get('nonce', None)
        amount = data.get('amount', None)

        subscriber = get_object_or_404(models.Subscriber, nonce=nonce)

        donation = models.Donation(
            amount=amount,
            nonce=nonce,
            subscriber=subscriber,
            payment_type='UPN',
            is_paid=False
        )
        donation.save()

        refrence = 'SI00 ' + str(donation.id).zfill(10)

        qr_svg = generate_upn_qr(
            subscriber.name,
            '',
            '',
            Decimal(amount),
            refrence,
            'Donacija DJND'
        )

        return Response({
            'qr_code': qr_svg,
            'reference': refrence,
            'iban': settings.IBAN,
            'to_name': settings.TO_NAME.strip(),
            'to_address1': settings.TO_ADDRESS1.strip(),
            'to_address2': settings.TO_ADDRESS2.strip()
        })


class Donate(views.APIView):
    """
    GET get client token

    POST json data:
     - nonce
     - amount
    """
    authentication_classes = [authentication.SubscriberAuthentication]
    def get(self, request):
        return Response({'token': payment.client_token()})

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

        # if nonce not present deny
        if not nonce:
            return Response({'msg': 'Missing nonce.'}, status=status.HTTP_400_BAD_REQUEST)

        # if email not present, try to pay
        if not email:
            # if no amount deny
            if not amount:
                return Response({'msg': 'Missing amount.'}, status=status.HTTP_400_BAD_REQUEST)

            result = payment.pay_bt_3d(nonce, float(amount), taxExempt=True)
            if result.is_success:
                # create donation with subscriber
                subscriber = models.Subscriber.objects.get(nonce=nonce)

                # if dnation already created in UPN tab
                ex_donation = models.Donation.objects.filter(nonce=nonce)
                if ex_donation:
                    donation = ex_donation[0]
                    donation.payment_type = 'BT'
                    donation.is_paid = True
                else:
                    donation = models.Donation(
                        amount=amount,
                        nonce=nonce,
                        subscriber = subscriber,
                    )
                donation.save()

                return Response({
                    'msg': 'Thanks <3',
                    'nonce': nonce,
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
            subscriber.nonce = nonce
            subscriber.save()
        else:
            # subscriber does not exist on mautic
            subscriber = models.Subscriber.objects.create(
                name=name,
                address=address,
                nonce=nonce
            )
            subscriber.save()
            response, response_status = subscriber.save_to_mautic(email, send_email=False)
            if response_status != 200:
                # something went wrong with saving to mautic, abort
                return Response({'msg': response}, status=response_status)
            mautic_id = subscriber.mautic_id

        # add to mailing if they agreed
        if add_to_mailing:
            segment_id = settings.SEGMENTS.get('donations', None)
            response, response_status = mautic_api.addContactToASegment(segment_id, mautic_id)

        # Send email thanks for donation
        response, response_status = mautic_api.sendEmail(
            settings.MAIL_TEMPLATES['DONATION_WITHOUT_GIFT'],
            subscriber.mautic_id,
            {}
        )

        try:
            msg = ( name if name else 'Dinozaverka' ) + ' nam je podarila donacijo v višini: ' + str(donation.amount)
            sc.api_call(
                "chat.postMessage",
                json={
                    'channel': "#danesjenovdan_si",
                    'text': msg
                }
            )
        except:
            pass

        return Response({
            'msg': 'Thanks <3'
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

        # if nonce not present deny
        if not nonce:
            return Response({'msg': 'Missing nonce.'}, status=status.HTTP_400_BAD_REQUEST)

        # if email not present, try to pay
        if not email:
            # if no amount deny
            if not amount:
                return Response({'msg': 'Missing amount.'}, status=status.HTTP_400_BAD_REQUEST)

            result = payment.create_subscription(nonce, float(amount))
            if result.is_success:
                # create donation without subscriber
                subscriber = models.Subscriber.objects.get(nonce=nonce)
                donation = models.Donation(
                    amount=amount,
                    nonce=nonce,
                    subscriber = subscriber
                )
                donation.save()

                return Response({
                    'msg': 'Thanks <3',
                    'nonce': nonce,
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
            subscriber.nonce = nonce
            subscriber.save()
        else:
            # subscriber does not exist on mautic
            subscriber = models.Subscriber.objects.create(
                name=name,
                address=address,
                nonce=nonce
            )
            subscriber.save()
            response, response_status = subscriber.save_to_mautic(email, send_email=False)
            if response_status != 200:
                # something went wrong with saving to mautic, abort
                return Response({'msg': response}, status=response_status)
            mautic_id = subscriber.mautic_id

        # add to mailing if they agreed
        if add_to_mailing:
            segment_id = settings.SEGMENTS.get('donations', None)
            response, response_status = mautic_api.addContactToASegment(segment_id, mautic_id)

        # Send email thanks for donation
        response, response_status = mautic_api.sendEmail(
            settings.MAIL_TEMPLATES['DONATION_WITHOUT_GIFT'],
            subscriber.mautic_id,
            {}
        )

        try:
            msg = ( name if name else 'Dinozaverka' ) + ' nam je podarila mesečno donacijo v višini: ' + str(donation.amount)
            sc.api_call(
                "chat.postMessage",
                json={
                    'channel': "#danesjenovdan_si",
                    'text': msg
                }
            )
        except:
            pass

        return Response({
            'msg': 'saved'
        })

    def update(self, request):
        return Response({})


class DonationsStats(views.APIView):
    def get(self, request):
        return Response({
            'donations': models.Donation.objects.count(),
            'collected': sum(models.Donation.objects.values_list('amount', flat=True)),
            'max-donation': max(models.Donation.objects.values_list('amount', flat=True))
        })


class ImageViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    lookup_field = 'token'
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
