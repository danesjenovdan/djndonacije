from django.views.generic import TemplateView
from djnd_supporters import models, payment

class TestPaymentView(TemplateView):
    template_name = "test_payment.html"

    def get_context_data(self, *args, **kwargs):
        context = super(TestPaymentView, self).get_context_data(*args, **kwargs)
        supporter = models.Supporter.objects.get(id=1)
        context['token'] = payment.client_token(supporter)
        return context
