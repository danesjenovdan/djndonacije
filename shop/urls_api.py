from django.conf.urls import url
from shop import api

urlpatterns = [
    url(r'^products/(?P<pk>\d+)/', api.ProductsList.as_view()),
    url(r'^products/', api.ProductsList.as_view()),
    url(r'^categories/', api.CategoryList.as_view()),
    url(r'^items/(?P<pk>\d+)/', api.ItemView.as_view()),
    url(r'^items/', api.ItemView.as_view()),
    url(r'^add_to_basket/', api.add_to_basket),
    url(r'^basket/', api.basket),
    url(r'^checkout/', api.Checkout.as_view()),
    url(r'^pay/', api.Pay.as_view()),
    url(r'^clear/', api.clear_session),
    ]
