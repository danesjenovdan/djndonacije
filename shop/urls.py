#from django.conf.urls import url
from django.urls import path, re_path

from . import views

urlpatterns = [
    path("poloznica/", views.poloznica),
    re_path(
        r'^upn_pdf/(?P<pk>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,:\_]+)',
        views.getPDFodOrder,
    ),
    # path('braintree-test/', views.bt_test)
]
