from djnd_supporters.mautic_api import MauticApi
import braintree
from datetime import datetime, timedelta
from django.conf import settings
from djnd_supporters import models

mautic_api = MauticApi()

def add_user_to_mautic(email, name, password, segment_id):
    """
    add user to mautic
    arguments:
        email
        name
        password
    returns:
        if success
            mautic_id
        else
            None
    """
    response_contact, response_status = mautic_api.createContact(
        email=email,
        name=name,
        password=password
    )
    if response_status == 200:
        mautic_id = response_contact['contact']['id']
        response, response_status = mautic_api.addContactToASegment(segment_id, mautic_id)
        return mautic_id
    else:
        return None

def send_email(email_id, contact_id, municipality, username):
    """
    send_email to contact
    arguments:
        email_id: mautic email id
        contact_id: mautic contact id
        municipality: municipality name
    """
    response, response_status = mautic_api.sendEmail(
        email_id=email_id,
        contact_id=contact_id,
        data={
            'tokens': {
                'municipality': municipality,
                'username': username
            }
        })
    return response_status


def import_emails(emails, segment):
    from djnd_supporters import models
    count = len(emails)
    for i, email in enumerate(emails):
        print(f'adding {i} of {count}')
        response, response_status = mautic_api.getContactByEmail(email)
        if response_status == 200:
            contacts = response['contacts']
            if contacts:
                mautic_id = list(contacts.keys())[0]
                mautic_api.addContactToASegment(segment, mautic_id)
            else:
                subscriber = models.Subscriber.objects.create()
                subscriber.save()
                response, response_status = subscriber.save_to_mautic(email)
                mautic_api.addContactToASegment(segment, subscriber.mautic_id)

def export_bt():
    to_month = datetime.today()
    from_month = (datetime.today()-timedelta(days=28))
    data = []
    gateway = settings.GATEWAY
    search_results=gateway.transaction.search(
        braintree.TransactionSearch.disbursement_date.between(
            datetime(day=1, month=from_month.month, year=from_month.year),
            (datetime(day=1, month=to_month.month, year=to_month.year)-timedelta(days=1))
        )
    )
    for result in search_results:
        tt = models.Transaction.objects.filter(transaction_id=result.id).first()
        if tt:
            campaign = tt.campaign.name
        else:
            campaign = '?'
        temp = {
            'campaign': campaign,
            'transaction_id': result.id,
            'subscription_id': result.subscription_id,
            'transaction_status': result.type,
            'created_date': result.created_at.isoformat(),
            'amount_submitted_for_settlement': result.amount,
            'amount_authorized': result.amount,
            'payment_instrument_type': result.payment_instrument_type
        }
        for status in result.status_history:
            temp[f'{status.status}_date']: status.timestamp.isoformat()
            temp[f'{status.status}_amount']: status.amount
        data.append(temp)

    return data

def export_old_bt():
    data = []
    gateway = braintree.BraintreeGateway(
        braintree.Configuration(
            braintree.Environment.Production,
            merchant_id=settings.MERCHANT_ID,
            public_key=settings.PUBLIC_KEY,
            private_key=settings.PRIVATE_KEY
        )
    )
    search_results=gateway.transaction.search(
        braintree.TransactionSearch.disbursement_date.between(
            datetime(day=1, month=12, year=2023),
            (datetime(day=1, month=1, year=2024)-timedelta(days=1))
        )
    )
    for result in search_results:
        tt = models.Donation.objects.filter(transaction_id=result.id).first()
        if tt:
            campaign = tt.campaign
            temp = {
                'campaign': campaign.name,
                'transaction_id': result.id,
                'subscription_id': result.subscription_id,
                'transaction_status': result.type,
                'created_date': result.created_at.isoformat(),
                'amount_submitted_for_settlement': result.amount,
                'amount_authorized': result.amount,
                'payment_instrument_type': result.payment_instrument_type
            }
            for status in result.status_history:
                temp[f'{status.status}_date']: status.timestamp.isoformat()
                temp[f'{status.status}_amount']: status.amount
            data.append(temp)
        else:
            rd = models.RecurringDonation.objects.filter(subscription_id=result.subscription_id).first()
            if rd:
                campaign = rd.campaign
                if campaign:
                    campaign = campaign.name
                else:
                    campaign = 'DJND?'
                temp = {
                    'campaign': campaign,
                    'transaction_id': result.id,
                    'subscription_id': result.subscription_id,
                    'transaction_status': result.type,
                    'created_date': result.created_at.isoformat(),
                    'amount_submitted_for_settlement': result.amount,
                    'amount_authorized': result.amount,
                    'payment_instrument_type': result.payment_instrument_type
                }
                for status in result.status_history:
                    temp[f'{status.status}_date']: status.timestamp.isoformat()
                    temp[f'{status.status}_amount']: status.amount
                data.append(temp)

    return data

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip