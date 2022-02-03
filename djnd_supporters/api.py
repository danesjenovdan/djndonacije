from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import status, views, permissions, mixins, viewsets
from rest_framework.response import Response

from djnd_supporters import models, mautic_api, authentication, serializers
from djndonacije import payment
from djndonacije.slack_utils import send_slack_msg

from datetime import datetime

import requests
import braintree

from djnd_supporters.views import getPDForDonation
from django.template.loader import get_template
from django.core import signing

from sentry_sdk import capture_message


class GetOrAddSubscriber(views.APIView):
    def get_subscriber_id(self, email):
        mautic_id = None
        response, response_status = mautic_api.getContactByEmail(email)
        if response_status == 200:
            contacts = response['contacts']
            if contacts:
                mautic_id = list(contacts.keys())[0]
            else:
                subscriber = models.Subscriber.objects.create()
                subscriber.save()
                response, response_status = subscriber.save_to_mautic(email)
                if response_status != 200:
                    return Response({'msg': response}, status=response_status)
                else:
                    mautic_id = subscriber.mautic_id
        return mautic_id

class Subscribe(views.APIView):
    """
    Add subscriber od edit subscriptions
    POST:
        email
        segment / če pride zraven segment overide-i segment iz campaigna
        campaign
    """
    def post(self, request, format=None):
        data = request.data
        email = data.get('email', None)
        segment = data.get('segment_id', None)
        campaign = data.get('campaign_id', None)

        if campaign:
            campaign = models.DonationCampaign.objects.filter(id=campaign).first()

        # segment from argument has priority on segment from campaign
        if not segment and campaign:
            if campaign.segment:
                segment = campaign.segment

        if email:
            response, response_status = mautic_api.getContactByEmail(email)
            if response_status == 200:
                contacts = response['contacts']
                if contacts:
                    # user already exists on mautic
                    mautic_id = list(contacts.keys())[0]
                    mail_to_send = None
                    if segment:
                        # user is not on a segment then welcome mail
                        response, response_status = mautic_api.getSegmentsOfContact(mautic_id)
                        if response_status == 200:
                            segments = response['lists'].keys()
                            if segments and segment in segments.keys():
                                mail_to_send = 'edit'
                            else:
                                mail_to_send = 'welcome'
                                mautic_api.addContactToASegment(segment, mautic_id)

                    if campaign:
                        if mail_to_send == 'edit' and campaign.edit_subscriptions_email_tempalte:
                            email_id = campaign.edit_subscriptions_email_tempalte
                        elif mail_to_send == 'welcome':
                            if campaign.welcome_email_tempalte:
                                email_id = campaign.welcome_email_tempalte
                            elif campaign.edit_subscriptions_email_tempalte:
                                email_id = campaign.edit_subscriptions_email_tempalte
                            else:
                                capture_message(f'Campaign {campaign.name} has empty edit_subscriptions_email_tempalte and welcome_email_tempalte')

                        response, response_status = mautic_api.sendEmail(
                            email_id,
                            mautic_id,
                            {
                            }
                        )
                        return Response({'msg': 'mail sent'})
                    else:
                        capture_message(f'Each segment needs to belong to campaign')
                        return Response({'msg': 'mail not sent'})

                else:
                    # user does not exist on mautic, create new
                    subscriber = models.Subscriber.objects.create()
                    subscriber.save()
                    response, response_status = subscriber.save_to_mautic(email)
                    if response_status != 200:
                        return Response({'msg': response}, status=response_status)
                    else:
                        if segment:
                            mautic_api.addContactToASegment(segment, subscriber.mautic_id)

                        if campaign and campaign.welcome_email_tempalte:
                            response, response_status = mautic_api.sendEmail(
                                campaign.welcome_email_tempalte,
                                subscriber.mautic_id,
                                {}
                            )
                            return Response({'msg': 'mail sent'})
                        else:
                            # TODO think about this case
                            pass
                            return Response({'msg': 'mail not sent'})
            else:
                return Response({'msg': response}, status=response_status)
        return Response({'error': 'Missing email and/or token.'}, status=status.HTTP_409_CONFLICT)


class ManageSegments(views.APIView):
    """
    POST/DELETE

    /campaigns/<campaign>/contact/<token>
    campaign: name of campaign
    token: user token
    """
    authentication_classes = [authentication.SubscriberAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, segment, format=None):
        contact_id = request.user.mautic_id
        segment_id = settings.SEGMENTS.get(segment, None)
        if not segment_id:
            return Response({'msg': 'Segment doesnt exist'}, status=status.HTTP_404_NOT_FOUND)

        if contact_id:
            response, response_status = mautic_api.addContactToASegment(segment_id, contact_id)
            if response_status == 200:
                return Response(response)
            else:
                return Response(response, status=response_status)
        else:
            return Response({'msg': 'Subscriber doesnt exist'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, segment, format=None):
        contact_id = request.user.mautic_id
        segment_id = settings.SEGMENTS.get(segment, None)
        if not segment_id:
            return Response({'msg': 'Segment doesnt exist'}, status=status.HTTP_404_NOT_FOUND)

        if contact_id:
            response, response_status = mautic_api.removeContactFromASegment(segment_id, contact_id)
            if response_status == 200:
                return Response(response)
            else:
                return Response({'msg': response}, status=response_status)
        else:
            return Response({'msg': 'Subscriber doesnt exist'}, status=status.HTTP_404_NOT_FOUND)


class Segments(views.APIView):
    authentication_classes = [authentication.SubscriberAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        response, response_status = mautic_api.getSegments()
        if response_status == 200:
            return Response({'segments': [value for id, value in response['lists'].items()]})
        else:
            return Response({'msg': response}, status=response_status)


class UserSegments(views.APIView):
    authentication_classes = [authentication.SubscriberAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        contact_id = request.user.mautic_id
        response, response_status = mautic_api.getSegmentsOfContact(contact_id)
        if response_status == 200:
            segments = response['lists']
            if segments:
                return Response({'segments': [value for id, value in segments.items()]})
            else:
                return Response({'segments': []})
        else:
            return Response({'msg': response}, status=response_status)


class DonationsStats(views.APIView):
    def get(self, request):
        return Response({
            'donations': models.Transaction.objects.filter(created__gte=datetime(day=1, month=12, year=2020)).count(),
            'collected': sum(models.Transaction.objects.filter(created__gte=datetime(day=1, month=12, year=2020).values_list('amount', flat=True))),
            'max-donation': max(models.Transaction.objects.filter(created__gte=datetime(day=1, month=12, year=2020).values_list('amount', flat=True)))
        })


class ImageViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    lookup_field = 'token'
    queryset = models.Image.objects.filter(created__gte=datetime(day=1, month=12, year=2020))
    serializer_class = serializers.ImageSerializer


class AgrumentMailApiView(views.APIView):
    def post(self, request):
        data = request.data
        if settings.AGRUM_TOKEN != request.META.get('HTTP_AUTHORIZATION', None):
            return Response({
                    'msg': 'You have no permissions for do that.'
                }, status=403)
        short_url_response = requests.get('https://djnd.si/yomamasofat/?fatmama=%s' % data['url'])
        if short_url_response:

            email_id = int(data.get('email_template_id', 42))

            # get tempalte of email
            response, response_status = mautic_api.getEmail(email_id)

            # make changes in email
            content = response["email"]["customHtml"]
            content = content.replace('{content}', data['content_html'])
            content = content.replace('{image}', data['image_url'])
            content = content.replace('{short_url}', short_url_response.text)

            content = content.replace('{source_name}', data.get('image_source', ''))
            content = content.replace('{source_url}', data.get('image_source_url', ''))

            # create new email
            response, response_status = mautic_api.createEmail(
                "Agrument: " + data['title'],
                data['title'],
                data['title'],
                customHtml=content,
                emailType='list',
                description="Agrument",
                assetAttachments=None,
                template='cards',
                lists=[1],
                fromAddress='agrument@posta.danesjenovdan.si',
                fromName='Agrument'
            )
            if response_status == 200:
                new_email_id = response['email']['id']

                if response_status == 200:
                    #print(mautic_api.sendEmail(42, 315, {
                    #    'tokens': {
                    #        "content": data['content_html'],
                    #        "image": data['image_url'],
                    #        "short_url": short_url_response.text
                    #    }
                    #}))
                    print(
                        mautic_api.sendEmailToSegment(
                            new_email_id, {}
                        )
                    )
                else:
                    return Response({
                        'msg': 'cannot send email'
                        },
                        status=409
                    )
            else:
                return Response({
                    'msg': 'cannot send email'
                    },
                    status=409
                )
        return Response({
            'msg': 'sent'
        })


class DonationCampaignStatistics(views.APIView):
    """
    GET get statistics of campaign
    """
    authentication_classes = [authentication.SubscriberAuthentication]
    def get(self, request, campaign_id=0):
        donation_campaign = get_object_or_404(models.DonationCampaign, pk=campaign_id)
        donations = donation_campaign.donations.filter(is_paid=True)
        return Response({
            'donation-amount': sum([d.get_amount() for d in donations]),
            'donation-count': donations.count()
        })


class GenericDonationCampaign(views.APIView):
    """
    GET get client token and donation specifics

    POST json data:
     - nonce
     - amount
     - email
     - name
     - mailing
     - address
     - payment_type
    """
    authentication_classes = [authentication.SubscriberAuthentication]
    def get(self, request, campaign_id=0):
        print(campaign_id)
        customer_id = request.GET.get('customer_id', None)
        if customer_id:
            subscriber = models.Subscriber.objects.filter(customer_id=customer_id)
            if subscriber:
                subscriber = subscriber[0]
            else:
                subscriber = None
        else:
            subscriber = None

        donation_campaign = get_object_or_404(models.DonationCampaign, pk=campaign_id)
        donation_obj = serializers.DonationCampaignSerializer(donation_campaign).data
        donation_obj.update(payment.client_token(subscriber))
        return Response(donation_obj)

    def post(self, request, campaign_id=0):
        data = request.data
        nonce = data.get('nonce', None)
        amount = data.get('amount', None)
        email = data.get('email', None)
        name = data.get('name', '')
        add_to_mailing = data.get('mailing', False)
        address = data.get('address', '')
        payment_type = data.get('payment_type', 'braintree')

        donation_campaign = get_object_or_404(models.DonationCampaign, pk=campaign_id)

        # if no amount deny
        if not amount:
            return Response({'msg': 'Missing amount.'}, status=status.HTTP_400_BAD_REQUEST)

        # email and nonce are both present
        response, response_status = mautic_api.getContactByEmail(email)
        if response_status == 200:
            contacts = response['contacts']
        else:
            # something went wrong with mautic, return
            return Response({'msg': response}, status=response_status)
        print(contacts)
        mautic_id = None
        if contacts:
            # subscriber exists on mautic
            mautic_id = list(contacts.keys())[0]
            subscriber = models.Subscriber.objects.get(mautic_id=mautic_id)
            subscriber.name = name
            subscriber.address = address
            subscriber.save()
        else:
            # subscriber does not exist on mautic
            subscriber = models.Subscriber.objects.create(name=name, address=address)
            subscriber.save()
            response, response_status = subscriber.save_to_mautic(email)
            if response_status != 200:
                # something went wrong with saving to mautic, abort
                return Response({'msg': response}, status=response_status)
            mautic_id = subscriber.mautic_id

        # add to mailing if they agreed
        if add_to_mailing and donation_campaign.add_to_mailing:
            response, response_status = mautic_api.addContactToASegment(donation_campaign.add_to_mailing, mautic_id)


        if payment_type == 'upn':
            # check if campaign supports upn payments
            if not donation_campaign.has_upn:
                return Response({'msg': 'This campaign does not support UPN payments.'}, status=status.HTTP_400_BAD_REQUEST)
            donation = models.Transaction(
                amount=amount,
                nonce=nonce,
                subscriber=subscriber,
                is_paid=False,
                payment_method='upn',
                campaign=donation_campaign)
            donation.save()
            reference = 'SI00 11' + str(donation.id).zfill(8)
            donation.reference = reference
            donation.save()

            pdf = getPDForDonation(None, donation.id).render().content

            response, response_status = mautic_api.saveFile('upn.pdf', pdf)
            response, response_status = mautic_api.saveAsset('upn', response['file']['name'])
            asset_id = response['asset']['id']

            email_id = donation_campaign.upn_email_template

            response, response_status = mautic_api.getEmail(email_id)
            content = response["email"]["customHtml"]
            subject = response["email"]["subject"]
            response_mail, response_status = mautic_api.createEmail(
                subject + ' copy-for ' + name,
                subject,
                subject,
                customHtml=content,
                #emailType='list',
                description='email for donation with UPN',
                assetAttachments=[asset_id],
                template='cards',
                #lists=[1],
                fromAddress=response["email"]["fromAddress"],
                fromName=response["email"]["fromName"]
            )


            mautic_api.sendEmail(
                response_mail['email']['id'],
                mautic_id,
                {})


        elif payment_type == 'braintree':
            # check if campaign supports braintree payments
            if not donation_campaign.has_braintree:
                return Response({'msg': 'This campaign does not support braintree payments.'}, status=status.HTTP_400_BAD_REQUEST)

            result = payment.pay_bt_3d(
                nonce,
                float(amount),
                taxExempt=True,
                description=donation_campaign.name,
                campaign=donation_campaign.name,
            )
            if result.is_success:
                transaction_id = result.transaction.id
                payment_instrument_type = result.transaction.payment_instrument_type
                if payment_instrument_type == 'paypal_account':
                    payment_method = 'braintree-paypal'
                else:
                    payment_method = 'braintree'
                # create donation and image object without subscriber
                donation = models.Transaction(
                    amount=amount,
                    nonce=nonce,
                    subscriber=subscriber,
                    campaign=donation_campaign,
                    transaction_id=transaction_id,
                    payment_method=payment_method)
                donation.save()

                # send email if tempalte is setted in donation campaign
                if donation_campaign.bt_email_template:
                    response, response_status = mautic_api.sendEmail(
                        donation_campaign.bt_email_template,
                        subscriber.mautic_id,
                        {}
                    )
            else:
                return Response({'msg': result.message}, status=status.HTTP_400_BAD_REQUEST)


        # send slack msg
        try:
            name = name.split(' ')[0]
        except:
            pass

        msg = ( name if name else 'Dinozaverka' ) + ' nam je podarila donacijo za [ ' + donation_campaign.name + ' ] v višini: ' + str(donation.amount)
        send_slack_msg(msg, donation_campaign.slack_report_channel)

        response = {
            'msg': 'Thanks <3',
        }
        if donation_campaign.has_upload_image:
            image = models.Image(donation=donation)
            image.save()
            response.update({
                'upload_token': image.token
            })


        return Response(response)


class GenericCampaignSubscription(views.APIView):
    """
    GET get client token

    POST json data:
     - nonce
     - amount
     - email
     - name
     - mailing
     - address
     - customer_id
    """
    authentication_classes = [authentication.SubscriberAuthentication]
    def post(self, request, campaign_id=0):
        data = request.data
        nonce = data.get('nonce', None)
        amount = data.get('amount', None)
        email = data.get('email', None)
        name = data.get('name', '')
        add_to_mailing = data.get('mailing', False)
        address = data.get('address', '')
        customer_id = data.get('customer_id', '')
        token = data.get('token', None)

        donation_campaign = get_object_or_404(models.DonationCampaign, pk=campaign_id)

        # get user with this email from mautic
        response, response_status = mautic_api.getContactByEmail(email)
        if response_status == 200:
            contacts = response['contacts']
        else:
            # something went wrong with mautic, return
            return Response({'msg': response}, status=response_status)

        print(contacts)
        mautic_id = None
        if contacts:
            # subscriber exists on mautic
            mautic_id = list(contacts.keys())[0]
            subscriber = models.Subscriber.objects.filter(mautic_id=mautic_id)
            if subscriber:
                subscriber = subscriber[0]
                if customer_id and subscriber.customer_id != customer_id:
                    # TODO sentry log error, maybe wee need to merge people for some special cases?
                    subscriber.customer_id = customer_id
                subscriber.name = name
                subscriber.address = address
                subscriber.save()
            else:
                if customer_id:
                    subscriber = models.Subscriber.objects.get(customer_id=customer_id)
                    subscriber.mautic_id = mautic_id
                    subscriber.save()
                else:
                    # TODO sentry log error
                    return Response({'msg': 'WTF'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            # subscriber does not exist on mautic
            if customer_id:
                subscriber, created = models.Subscriber.objects.get_or_create(customer_id=customer_id)
                subscriber.name = name
                subscriber.name = address
            else:
                subscriber = models.Subscriber.objects.create(name=name, address=address)
            subscriber.save()
            response, response_status = subscriber.save_to_mautic(email)
            if response_status != 200:
                # something went wrong with saving to mautic, abort
                return Response({'msg': response}, status=response_status)
            mautic_id = subscriber.mautic_id

        # add to mailing if they agreed
        if add_to_mailing and donation_campaign.add_to_mailing:
            response, response_status = mautic_api.addContactToASegment(donation_campaign.add_to_mailing, mautic_id)

        # check if campaign supports braintree payments
        if not donation_campaign.has_braintree_subscription:
            return Response({'msg': 'This campaign does not support braintree payments.'}, status=status.HTTP_400_BAD_REQUEST)

        # get plan id from campaign
        plan_id = donation_campaign.braintee_subscription_plan_id
        if not plan_id:
            plan_id = 'djnd'

        # create and save subscription if success
        result = payment.create_subscription(nonce, customer_id, plan_id=plan_id, costum_price=amount)
        if result.is_success:
            # create donation without subscriber
            donation = models.Subscription(
                amount=amount,
                subscriber=subscriber,
                subscription_id=result.subscription.id,
                campaign=donation_campaign,
                token=nonce,
                is_active=True
            )
            donation.save()
            if donation_campaign.bt_subscription_email_template:
                response, response_status = mautic_api.sendEmail(
                    donation_campaign.bt_subscription_email_template,
                    subscriber.mautic_id,
                    {}
                )
        else:
            return Response({'msg': result.message}, status=status.HTTP_400_BAD_REQUEST)

        # send slack msg
        try:
            name = name.split(' ')[0]
        except:
            pass

            msg = ( name if name else 'Dinozaverka' ) + ' nam je podarila mesecno donacijo za ' + donation_campaign.name + ' v višini: ' + str(donation.amount)
            send_slack_msg(msg, donation_campaign.slack_report_channel)

        return Response({
            'msg': 'Thanks <3',
            'subscription_id': result.subscription.id,
            'user_token': subscriber.token,
            'subscription_token': nonce,
        })


class CancelSubscription(views.APIView):
    """
    POST json data:
     - token
     - customer_id
     - subscription_id
    """
    authentication_classes = [authentication.SubscriberAuthentication]
    def post(self, request):
        data = request.data

        token = data.get('token', None)
        customer_id = data.get('customer_id', None)
        subscription_id = data.get('subscription_id', None)

        if token:
            subscriber = get_object_or_404(
                models.Subscriber,
                token=token
            )
        elif customer_id:
            subscriber = get_object_or_404(
                models.Subscriber,
                customer_id=customer_id
            )
        else:
            return Response(
                {
                    'msg': 'You need to post customer_id or token of user.'
                },
                status=409
            )

        subscription = get_object_or_404(
            models.Subscription,
            subscription_id=subscription_id
        )
        if subscription.subscriber == subscriber:
            result = payment.cancel_subscription(subscription_id)
            print(vars(result))
            if result.is_success:
                #subscription.subscription_id = None
                subscription.is_active = False
                subscription.save()
                return Response(
                    {
                        'msg': 'subscription canceled'
                    }
                )
            else:
                return Response(
                    {
                        'msg': result.message
                    }
                )
        else:
            return Response(
                {
                    'msg': 'You dont have permissions for cancel subscription'
                },
                status=403
            )


class BraintreeWebhookApiView(views.APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        webhook_notification = payment.get_hook(str(data['bt_signature']), data['bt_payload'])
        subscription = None

        event = webhook_notification.kind
        try:
            subscription_id = webhook_notification.subject['subscription']['id']
            if event == braintree.WebhookNotification.Kind.SubscriptionChargedSuccessfully:
                for transaction in webhook_notification.subject['subscription']['transactions']:
                    if transaction['processor_response_text'] == 'Approved' and transaction['status'] == 'submitted_for_settlement':
                        print('create_transaction')
                        subscription = models.Subscription.objects.filter(subscription_id=subscription_id).first()
                        transaction_id = transaction['id']
                        new_transaction = models.Transaction(
                            amount=transaction['amount'],
                            subscriber=subscription.subscriber,
                            campaign=subscription.campaign,
                            transaction_id=transaction_id,
                            payment_method='braintree-subscription'
                        )
                        new_transaction.save()
                        if subscription.campaign.subscription_charged_successfully:
                            response, response_status = mautic_api.sendEmail(
                                subscription.campaign.subscription_charged_successfully,
                                subscription.subscriber.mautic_id,
                                {}
                            )
                        if subscription.campaign.web_hook_url:
                            requests.post(
                                subscription.campaign.web_hook_url,
                                json={
                                    'amount': transaction['amount'],
                                    'subscription_id': subscription_id,
                                    'customer_id': subscription.subscriber.customer_id,
                                    'kind': 'subscription_charged_successfully',
                                }
                            )

            elif event == braintree.WebhookNotification.Kind.SubscriptionChargedUnsuccessfully:
                subscription_id = webhook_notification.subject['subscription']['id']
                subscription = models.Subscription.objects.filter(subscription_id=subscription_id).first()
                campagin = subscription.campaign
                if campagin.charged_unsuccessfully_email:
                    response, response_status = mautic_api.sendEmail(
                        campagin.charged_unsuccessfully_email,
                        subscription.subscriber.mautic_id,
                        {}
                    )

            elif event == braintree.WebhookNotification.Kind.SubscriptionCanceled:
                subscription_id = webhook_notification.subject['subscription']['id']
                subscription = models.Subscription.objects.filter(subscription_id=subscription_id).first()
                subscription.is_active = False
                subscription.save()
                campagin = subscription.campaign
                if campagin.subscription_canceled_email:
                    response, response_status = mautic_api.sendEmail(
                        campagin.subscription_canceled_email,
                        subscription.subscriber.mautic_id,
                        {}
                    )

        except Exception as e:
            print(e)
            # TODO send sentry error
            details = "UNKNOWN?"
            proj = None

        if subscription:
            send_slack_msg(f':bell:  Event "{event}" was triggered on braintree.', subscription.campaign.slack_report_channel)

        return Response(status=204)


class SendEmailApiView(GetOrAddSubscriber):
    """
    POST json data:
     - email
     - email_template_id

    Authorization:
        athorization token
    """
    def post(self, request, campaign_id=0):
        data = request.data
        email = data.get('email', None)
        email_template_id = data.get('email_template_id', None)
        token = request.META.get('HTTP_AUTHORIZATION')
        if token not in [settings.EMAIL_TOKEN, settings.AGRUM_TOKEN]:
            return Response({'msg': 'You dont have permissions for send emails'}, status=403)
        if not email or not email_template_id:
            return Response({'msg': 'Try again'}, status=status.HTTP_400_BAD_REQUEST)
        user_mautic_id = self.get_subscriber_id(email)
        mautic_api.sendEmail(email_template_id, user_mautic_id, {})
        return Response({'msg': 'mail sent'})


class CreateAndSendMailApiView(views.APIView):
    def post(self, request):
        data = request.data
        print(data)
        if settings.AGRUM_TOKEN != request.META.get('HTTP_AUTHORIZATION', None):
            return Response({
                    'msg': 'You have no permissions for do that.'
                }, status=403)

        email_data = {
            'name': data['title'],
            'title': data['title'],
            'subject': data['title'],
            'customHtml': data['content'],
            'emailType': 'list',
            'description': data["description"],
            'assetAttachments': None,
            'template': 'cards',
            'lists': data['segments'],
        }

        if 'fromName' in data.keys():
            email_data.update(fromName=data['fromName'])

        if 'fromAddress' in data.keys():
            email_data.update(fromAddress=data['fromAddress'])

        # create new email
        response, response_status = mautic_api.createEmail(**email_data)
        if response_status == 200:
            new_email_id = response['email']['id']

            if response_status == 200:
                #print(mautic_api.sendEmail(42, 315, {
                #    'tokens': {
                #        "content": data['content_html'],
                #        "image": data['image_url'],
                #        "short_url": short_url_response.text
                #    }
                #}))
                print(
                    mautic_api.sendEmailToSegment(
                        new_email_id, {}
                    )
                )
            else:
                return Response({
                    'msg': 'cannot send email'
                    },
                    status=409
                )
        else:
            return Response({
                'msg': response
                },
                status=409
            )
        return Response({
            'msg': 'sent'
        })
