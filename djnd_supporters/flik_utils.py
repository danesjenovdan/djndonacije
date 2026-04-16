from django.conf import settings

from djnd_supporters import flik, mautic_api, models

flik_auth_oob = flik.FlikAuth(
    api_key=settings.FLIK_OOB_API_KEY,
    shared_secret=settings.FLIK_OOB_SS,
    username=settings.FLIK_USERNAME,
    password=settings.FLIK_PASSWORD,
)


def create_flik_request(subscription):
    donation_campaign = subscription.campaign
    donation = models.Transaction(
        amount=subscription.amount,
        subscriber=subscription.subscriber,
        campaign=donation_campaign,
        payment_method="flik",
        is_paid=False,
    )
    donation.save()
    ip, phone_number = subscription.token.split("|")
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
    if email_template_id := donation_campaign.flik_subscription_request_email_template:
        mautic_api.sendEmail(email_template_id, subscription.subscriber.mautic_id, {})

    if flik_response.success:
        donation.reference = flik_response.purchase_id
        donation.save()

        return True
    else:
        raise Exception("Failed to initialize flik payment")
