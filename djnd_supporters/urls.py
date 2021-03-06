from rest_framework import routers
from django.urls import path, include

from djnd_supporters import api, views

router = routers.DefaultRouter()
router.register(r'images', api.ImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('subscribe/', api.Subscribe.as_view()),
    path('segments/', api.Segments.as_view()),
    path('segments/my/', api.UserSegments.as_view()),
    path('segments/<segment>/contact/', api.ManageSegments.as_view()),
    path('donate/', api.Donate.as_view()),
    path('monthly-donation/', api.RecurringDonate.as_view()),
    path('donations-stats/', api.DonationsStats.as_view()),
    path('send-agrument-mail/', api.AgrumentMailApiView.as_view()),

    path('users/', api.UsersImport.as_view()),

    path('test/', views.TestPaymentView.as_view()),
]
