from djnd_supporters import models
from rest_framework import authentication
from rest_framework import exceptions


class SubscriberAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        email = request.GET.get('email')
        token = request.GET.get('token')
        if not (email and token):
            return None
        try:
            subscriber = models.Subscriber.objects.get(token=token)
            # TODO check mautic if is equal email, make login session
        except models.Subscriber.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such subscriber')

        return (subscriber, None)
