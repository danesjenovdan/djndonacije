from rest_framework import routers
from django.urls import path, re_path, include

from djnd_supporters import api, views

router = routers.DefaultRouter()
router.register(r'images', api.ImageViewSet)
router.register(r'donation-campaign', api.DonationCampaignInfo)


urlpatterns = [
    path('', include(router.urls)),
    path('subscribe/', api.Subscribe.as_view()),
    path('segments/', api.Segments.as_view()),
    path('segments/my/', api.UserSegments.as_view()),
    path('segments/<segment>/contact/', api.ManageSegments.as_view()),
    path('donations-stats/', api.DonationsStats.as_view()),
    path('send-agrument-mail/', api.AgrumentMailApiView.as_view()),
    path('send-email/', api.SendEmailApiView.as_view()),
    path('create-and-send-custom-email/', api.CreateAndSendMailApiView.as_view()),
    re_path('generic-donation/subscription/(?:(?P<campaign_id>\w+)/)?$', api.GenericCampaignSubscription.as_view()),
    re_path('generic-donation/cancel-subscription/', api.CancelSubscription.as_view()),
    re_path('generic-donation/(?:(?P<campaign_id>\w+)/)?$', api.GenericDonationCampaign.as_view()),
    re_path('donation-statistics/(?:(?P<campaign_id>\w+)/)?$', api.DonationCampaignStatistics.as_view()),
    re_path('braintree-webhook/', api.BraintreeWebhookApiView.as_view()),
]
