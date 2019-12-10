from django.conf import settings

from rest_framework import status, views, permissions, mixins, viewsets
from rest_framework.response import Response

from djnd_supporters import models, mautic_api, authentication, serializers
from djndonacije import payment


class Subscribe(views.APIView):
    """
    This endpoint is for make braintree subscription
    """
    def post(self, request, format=None):
        data = request.data
        email = data.get('email', None)
        token = data.get('token', None)
        if token:
            subscriber = models.Subscriber.objects.get_or_create(token=token)
            return Response({'email': email, 'token': subscriber.token})
        if email:
            subscriber, created = models.Subscriber.objects.get_or_create(email=email)
            subscriber.save()
            subscriber.save_to_mautic(email)
            return Response({'email': email, 'token': subscriber.token})
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
            # TODO: if mautic fails return mautic response status
            return Response(mautic_api.addContactToASegment(segment_id, contact_id))
        else:
            return Response({'msg': 'Subscriber doesnt exist'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, segment, format=None):
        contact_id = request.user.mautic_id
        segment_id = settings.SEGMENTS.get(segment, None)
        if not segment_id:
            return Response({'msg': 'Segment doesnt exist'}, status=status.HTTP_404_NOT_FOUND)

        if contact_id:
            # TODO: if mautic fails return mautic response status
            return Response(mautic_api.removeContactFromASegment(segment_id, contact_id))
        else:
            return Response({'msg': 'Subscriber doesnt exist'}, status=status.HTTP_404_NOT_FOUND)


class Segments(views.APIView):
    authentication_classes = [authentication.SubscriberAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        return Response({'segments': [value for id, value in mautic_api.getSegments()['lists'].items()]})


class UserSegments(views.APIView):
    authentication_classes = [authentication.SubscriberAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        contact_id = request.user.mautic_id
        segments = mautic_api.getSegmentsOfContact(contact_id)['lists']
        if segments:
            return Response({'segments': [value for id, value in segments.items()]})
        else:
            return Response({'segments': []})


class Donate(views.APIView):
    """
    GET get client token

    POST json data:
     - nonce
     - amount
    """
    authentication_classes = [authentication.SubscriberAuthentication]
    def get(self, request):
        return Response({'token' :payment.client_token()})

    def post(self, request):
        data = request.data
        nonce = data.get('nonce', None)
        amount = data.get('amount', None)
        email = data.get('email', None)
        name = data.get('name', '')

        contacts = mautic_api.getContactByEmail(email)
        print(contacts)
        if contacts['contacts']:
            mautic_id = list(contacts['contacts'].keys())[0]
            subscriber = models.Subscriber.objects.get(mautic_id=mautic_id)
            subscriber.name = name
            subscriber.save()
        else:
            subscriber = None

        if ( not nonce ) or ( not amount):
            return Response({'msg': 'Nonce or amount are missing.'}, status=status.HTTP_409_CONFLICT)

        result = payment.pay_bt_3d(nonce, amount)
        print(result)
        if result.is_success:
            # crete donation and image object
            donation = models.Donation(amount=amount, subscriber=subscriber)
            donation.save()
            image = models.Image(donation=donation)
            image.save()
            return Response({
                'msg': 'Thanks <3',
                'upload_url': image.get_upload_url()
            })
        else:
            return Response({'msg': result.transaction.processor_response_text}, status=status.HTTP_400_BAD_REQUEST)


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

    def post(self, request):
        data = request.data
        nonce = data.get('nonce', None)
        gifts_amounts = data.get('gifts_amounts', [])
        email = data.get('email', None)
        amount = data.get('amount', None)

        contacts = mautic_api.getContactByEmail(email)
        print(contacts)
        if contacts['contacts']:
            mautic_id = list(contacts['contacts'].keys())[0]
            subscriber = models.Subscriber.objects.get(mautic_id=mautic_id)
        else:
            subscriber = None

        if ( not nonce ) or ( not amount):
            return Response({'msg': 'Nonce or amount are missing.'}, status=status.HTTP_409_CONFLICT)

        result = payment.pay_bt_3d(nonce, amount)
        print(result)
        new_subscribers = []
        if result.is_success:
            # crete donation and image object
            new_gift = models.Gift(amount=amount, subscriber=subscriber)
            new_gift.save()
            for gift_amount in gifts_amounts:
                new_subscriber = models.Subscriber.objects.create(email='')
                new_subscriber.save()
                donation = models.Donation(amount=gift_amount, subscriber=new_subscriber)
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
                'owner_token': subscriber.token,
                'gifts': new_subscribers
            })
        else:
            return Response({'msg': result.transaction.processor_response_text}, status=status.HTTP_400_BAD_REQUEST)


class AssignGift(views.APIView):
    def post(self, request):
        data = request.data
        owner_token = data.get('owner_token', None)

        gift_email = data.get('gift_email', None)
        subscriber_token = data.get('subscriber_token')
        name = data.get('name', None)
        message = data.get('message', None)

        #TODO check if gift is already assigned

        subscriber = models.Subscriber.objects.get(token=owner_token)

        new_subscriber = models.Subscriber.objects.get(token=subscriber_token)
        donation = subscriber.gifts.last().gifts.filter(subscriber=new_subscriber)
        if donation:
            donation = donation[0]
            mautic_id = None
            contacts = mautic_api.getContactByEmail(gift_email)
            if contacts['contacts']:
                print('contact ze obstaja')
                mautic_id = list(contacts['contacts'].keys())[0]
            else:
                print('dodaj novga')
                new_subscriber.name = name
                new_subscriber.save_to_mautic(gift_email, name=name, send_email=False)
                mautic_id = new_subscriber.mautic_id

            print(mautic_id)
            print(mautic_api.sendEmail(
                settings.MAIL_TEMPLATES['GIFT'],
                mautic_id,
                {
                    'tokens': {
                        'message': message,
                        '{upload_image}': donation.image.get_upload_url()
                    }
                }
            ))
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
