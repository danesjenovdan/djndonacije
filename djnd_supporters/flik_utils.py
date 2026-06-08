from django.conf import settings

from djnd_supporters import flik, models
from djnd_supporters.mautic_api import MauticApi

mautic_api = MauticApi()


def normalize_phone_number(phone_number):
    phone_number = phone_number.replace(" ", "")
    if phone_number[0] == "0" and len(phone_number) == 9:
        phone_number = "00386" + phone_number[1:]
    elif phone_number.startswith("+"):
        phone_number = phone_number.replace("+", "00")
    return phone_number


def create_flik_request(subscription):
    donation_campaign = subscription.campaign
    flik_api = donation_campaign.flik_api
    flik_auth_oob = flik.FlikAuth(
        api_key=flik_api.obb_api_key,
        shared_secret=flik_api.obb_shared_secret,
        username=flik_api.username,
        password=flik_api.password,
    )
    donation = models.Transaction(
        amount=subscription.amount,
        subscriber=subscription.subscriber,
        campaign=donation_campaign,
        account=flik_api.account,
        subscription=subscription,
        payment_method="flik-subscription",
        is_paid=False,
    )
    donation.save()
    ip, phone_number = subscription.token.split("|")
    phone_number = normalize_phone_number(phone_number)
    flik_response = flik.initialize_payment(
        transaction_id=donation.id,
        amount="{:.2f}".format(subscription.amount),
        description=donation_campaign.upn_name,
        shopper_locale="sl",
        customer_ip=ip,
        success_url=f"{settings.FRONTEND_URL}/{donation_campaign.slug}/doniraj/hvala?transaction_id={donation.id}",
        error_url=f"{settings.FRONTEND_URL}/{donation_campaign.slug}/doniraj/napaka",
        cancel_url=f"{settings.FRONTEND_URL}/{donation_campaign.slug}/doniraj/napaka",
        callback_url=f"{settings.BASE_URL}/api/flik-callback/",
        flik_auth=flik_auth_oob,
        phone_number=phone_number,
    )
    if flik_response.success:
        donation.reference = flik_response.purchase_id
        donation.save()
        if (
            email_template_id := donation_campaign.flik_subscription_request_email_template
        ):
            mautic_api.sendEmail(
                email_template_id, subscription.subscriber.mautic_id, {}
            )
        return True
    else:
        raise Exception("Failed to initialize flik payment")
