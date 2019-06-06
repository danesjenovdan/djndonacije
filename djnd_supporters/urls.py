from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from rest_framework import routers

from djnd_supporters import api, views

router = routers.DefaultRouter()
router.register(r'projects', api.ProjectViewSet)
router.register(r'supporters', api.PrepareSupporterViewSet)
router.register(r'gifts', api.PrepareGiftViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('subscribe/', api.Subscribe.as_view()),
    path('subsribers/', api.SubscriberApiView.as_view()),

    # test views
    path('test-payment/', views.TestPaymentView.as_view()),
]
