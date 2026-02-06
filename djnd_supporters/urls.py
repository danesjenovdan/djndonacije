from django.urls import include, path, re_path
from rest_framework import routers

from djnd_supporters import api, views

router = routers.DefaultRouter()
router.register(r"images", api.ImageViewSet)
router.register(r"donation-campaign", api.DonationCampaignInfo)


urlpatterns = [
    path("", include(router.urls)),
    path("subscribe/", api.Subscribe.as_view()),
    path("safe-subscribe/", api.SafeSubscribe.as_view()),
    path("segments/", api.Segments.as_view()),
    path("segments/my/", api.UserSegments.as_view()),
    path("segments/<segment>/contact/", api.ManageSegments.as_view()),
    path("donations-stats/", api.DonationsStats.as_view()),
    path("send-agrument-mail/", api.AgrumentMailApiView.as_view()),
    path("send-email/", api.SendEmailApiView.as_view()),
    path("create-and-send-custom-email/", api.CreateAndSendMailApiView.as_view()),
    path("subscriptions/my/", api.UserSubscriptions.as_view()),
    path("delete-all-user-data/", api.DeleteAllUserData.as_view()),
    re_path(
        "generic-donation/subscription/(?:(?P<campaign>[-\w]+)/)?$",
        api.GenericCampaignSubscription.as_view(),
    ),
    re_path("generic-donation/cancel-subscription/", api.CancelSubscription.as_view()),
    re_path(
        "generic-donation/(?:(?P<campaign>[-\w]+)/)?$",
        api.GenericDonationCampaign.as_view(),
    ),
    re_path(
        "donation-campaign/(?P<campaign>[-\w]+)/qrcode$",
        api.GenericDonationCampaignQRCode.as_view(),
    ),
    re_path(
        "donation-statistics/(?:(?P<campaign>[-\w]+)/)?$",
        api.DonationCampaignStatistics.as_view(),
    ),
    re_path(
        "donation-nonce/",
        api.DonationCampaignBraintreeNonce.as_view(),
    ),
    re_path("braintree-webhook/", api.BraintreeWebhookApiView.as_view()),
    re_path("transaction-export/", views.braintree_export, name="transaction-export"),
    re_path("flik-callback/", api.FlikCallback.as_view(), name="flik-callback"),
    path("test-upn/", views.TestUPNView.as_view()),
]
