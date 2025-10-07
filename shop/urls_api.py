from django.urls import path, re_path

from shop import api

urlpatterns = [
    path("products/<int:pk>/", api.ProductsList.as_view()),
    path("products/", api.ProductsList.as_view()),
    path("categories/", api.CategoryList.as_view()),
    path("items/<int:pk>/", api.ItemView.as_view()),
    path("items/", api.ItemView.as_view()),
    path("add_to_basket/", api.add_to_basket),
    path("basket/", api.basket),
    path("checkout/", api.Checkout.as_view()),
    path("pay/", api.Pay.as_view()),
    path("clear/", api.clear_session),
]
