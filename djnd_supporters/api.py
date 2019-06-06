from django.http import JsonResponse
from django.conf import settings

from rest_framework import viewsets, status, mixins, views
from rest_framework.response import Response

from djndonacije import payment
from djnd_supporters import models, mautic_api, serializers, authentication, permissions

from requests.auth import HTTPBasicAuth
from datetime import datetime

def getBasicAuth():
    return HTTPBasicAuth(settings.MAUTIC_USER, settings.MAUTIC_PASS)

def addSubscriber(request):
    email = request.POST.get('email')
    the_list = request.POST.get('the_list')
    subscriber = models.Subscriber.getOrCreate(email=email)
    mautic_api.addContactToACampaign(the_list, subscriber.mautic_id)
    return JsonResponse({'email': email, 'the_list': the_list})

def deleteSubscriber(request, token):
    subscriber = models.Subscriber.objects.filter(token=token)
    if subscriber:
        mautic_api.deleteContact(subscriber[0].mautic_id)
        subscriber[0].delete()
        return JsonResponse({'msg': 'Deleted'}, status=204)
    else:
        return JsonResponse({'msg': 'Subscriber doesnt exist'}, status=404)

def addToList(request):
    token = request.POST.get('token')
    the_list = request.POST.get('the_list')
    mautic_api.addContactToACampaign(the_list, subscriber.mautic_id)

def removeFromList(request):
    token = request.POST.get('token')
    the_list = request.POST.get('the_list')
    subscriber = models.Subscriber.objects.filter(token=token)
    if subscriber:
        return JsonResponse(mautic_api.removeContactToACampaign(the_list, subscriber.mautic_id))
    else:
        return JsonResponse({'msg': 'Subscriber doesnt exist'}, status=404)

def getSettings(request):
    token = request.POST.get('token')
    email = request.POST.get('email')
    subscriber = models.Subscriber.objects.filter(token=token, email=email)
    if subscriber:
        campaings = getCampaingOfMember(subscriber[0].mautic_id)
        return JsonResponse({
            'email': subscriber[0].email,
            'lists': [{
                'id': item['id'],
                'name': item['name']
                } for item in campaings['campaigns'].values()
            ]
        })
    else:
        return JsonResponse({'msg': 'Subscriber doesnt exist'}, status=404)

def deliverEmail(request):
    email = request.POST.get('email')
    subscriber = models.Subscriber.getOrCreate(email=email)
    mautic_api.sendEmail(
        email_id,
        contact_id,
        {'tokens':
            {
                'token': subscriber.token
            }
        }
    )
    return JsonResponse({'msg': 'sent'})

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer


class PrepareSupporterViewSet(mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.RetrieveModelMixin,
                              viewsets.GenericViewSet):
    queryset = models.Supporter.objects.all()
    serializer_class = serializers.SupporterSerializer
    permission_classes = (permissions.AnonCreateAndUpdateOwnerOnly,)
    authentication_classes = (authentication.SubscriberAuthentication,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # add braintree token to response
        supporter = models.Supporter.objects.get(email=request.data['email'])
        data = {'token': payment.client_token(supporter)}
        data.update(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        new_sum = sum([donation['amount'] for donation in data['donations']])

        if instance.donation_amount != new_sum and instance.subscription_id:
            payment.update_subscription(instance, costum_price=new_sum)

        self.perform_update(serializer)

        if not instance.subscription_id:
            data = {'token': payment.client_token(instance)}
            data.update(serializer.data)
        else:
            data = serializer.data
        return Response(data)


class PrepareGiftViewSet(mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    queryset = models.Gift.objects.all()
    serializer_class = serializers.GiftSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # add braintree token to response
        id_ = serializer.data.get('id')
        gift = models.Gift.objects.get(id=id_)
        data = {'token': payment.client_token(gift.sender)}
        data.update(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        new_sum = sum([donation['amount'] for donation in data['donations']])

        if instance.donation_amount != new_sum and instance.subscription_id:
            payment.update_subscription(instance, costum_price=new_sum)

        self.perform_update(serializer)

        if not instance.subscription_id:
            data = {'token': payment.client_token(instance)}
            data.update(serializer.data)
        else:
            data = serializer.data
        return Response(data)


class Subscribe(views.APIView):
    """
    This endpoint is for make braintree subscription
    """
    def post(self, request, format=None):
        data = request.data
        subscriber = models.Subscriber.objects.get(id=data.get('subscriber_id')).get_child()
        if subscriber.subscription_id:
            return Response({'msg': 'This subscriber already has a subscription.'}, status=status.HTTP_409_CONFLICT)
        amount = subscriber.donation_amount
        payment_response = payment.create_subscription(
            data.get('nonce'),
            subscriber,
            costum_price=amount
        )
        if payment_response.is_success:
            print(type(subscriber))
            if type(subscriber) == models.Supporter:
                # create contact and sand him welcome_mail
                subscriber.save_to_mautic()
            elif type(subscriber) == models.Gift:
                send_now = subscriber.send_at <= datetime.now().date()

                # if gift will be send now
                # create contact of gift recipient
                subscriber.save_to_mautic(send_email_to_sender=(not send_now))
                # create contact of gift sender and dont
                subscriber.sender.save_to_mautic(send_email=False)

                if send_now:
                    # this will be send mail to receiver and to sender
                    subscriber.send_gift()
            else:
                return Response({'msg': 'WTF'}, status=status.HTTP_409_CONFLICT)

            return Response({'msg': 'subscribed'})
        else:
            return Response(
                {
                    'msg': 'subscription failed',
                    'detail': payment_response
                },
                status=status.HTTP_409_CONFLICT
            )


class SubscriberApiView(views.APIView):
    """
    Endpoint for getting active Subscriber instances for this user
    """
    action = ('retrieve',)
    permission_classes = (permissions.permissions.IsAuthenticated,)
    authentication_classes = (authentication.SubscriberAuthentication,)

    def get(self, request, format=None):
        print(type(request.user))
        user = request.user.get_child()
        model_type = user.model_type
        supporter = []
        gifts = []
        if model_type == 'supporter':
            supporter = serializers.SupporterSerializer(user).data

        gifts = models.Gift.objects.filter(email=user.email)
        data = {
            "supporter": supporter,
            "received_gifts": serializers.GiftSerializer(gifts, many=True).data,
            "sent_gifts": serializers.GiftSerializer(user.gifts.all(), many=True).data if supporter else []
        }
        return Response(data)