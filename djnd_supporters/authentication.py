from djnd_supporters import models
from rest_framework import authentication
from rest_framework import exceptions

class SubscriberAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        email = request.GET.get('email')
        token = request.GET.get('token')
        print(email, token)
        if not (email and token):
            print(email, token)
            return None
        try:
            subscriber = models.Subscriber.objects.get(email=email, token=token)
        except models.Subscriber.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such subscriber')

        return (subscriber, None)