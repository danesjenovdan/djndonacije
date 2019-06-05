from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^poloznica/', views.poloznica),
    url(r'^upn_pdf/(?P<pk>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,:\_]+)', views.getPDFodOrder),
    url(r'^braintree-test/', views.bt_test)
]
