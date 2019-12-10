from django.views.generic import TemplateView
from djnd_supporters import models
from djndonacije import payment

class TestPaymentView(TemplateView):
    template_name = "test_payment.html"

    def get_context_data(self, *args, **kwargs):
        context = super(TestPaymentView, self).get_context_data(*args, **kwargs)
        context['token'] = payment.client_token()
        return context
