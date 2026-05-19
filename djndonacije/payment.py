import braintree

from djnd_supporters.models import BraintreeCustomer


def _get_environment(environment_name):
    return getattr(braintree.Environment, environment_name.capitalize())


def _build_gateway(braintree_api):
    if not braintree_api:
        raise Exception("No braintree credentials found")

    return braintree.BraintreeGateway(
        braintree.Configuration(
            environment=_get_environment(braintree_api.env),
            merchant_id=braintree_api.merchant_id,
            public_key=braintree_api.public_key,
            private_key=braintree_api.private_key,
        )
    )


def client_token(donation_campaign, user=None):
    gateway = get_gateway_from_campaign(donation_campaign)
    if not user:
        # create empty user
        result = gateway.customer.create({})
        return {
            "token": gateway.client_token.generate({"customer_id": result.customer.id}),
            "customer_id": result.customer.id,
        }
    if user:
        bt_customer = user.braintree_customers.filter(
            braintree_api=donation_campaign.braintree_api
        ).first()
        customer_id = bt_customer.customer_id if bt_customer else None
    else:
        # create empty user
        result = gateway.customer.create({})
        if result.is_success:
            bt_customer = BraintreeCustomer.objects.create(
                user=user,
                braintree_api=donation_campaign.braintree_api,
                customer_id=result.customer.id,
            )
            customer_id = bt_customer.customer_id
    return {
        "token": gateway.client_token.generate({"customer_id": customer_id}),
        "customer_id": customer_id,
    }


def create_subscription(
    gateway,
    nonce,
    customer_id,
    plan_id="djnd",
    costum_price=None,
    merchant_account_id=None,
):
    data = {
        "payment_method_nonce": nonce,
        "plan_id": plan_id,
    }
    if merchant_account_id:
        data.update(merchant_account_id=merchant_account_id)

    if costum_price:
        print(costum_price)
        data.update(
            {
                "price": "%.2f" % (float(costum_price)),
            }
        )

    print("PAYMENT: ", data)
    return gateway.subscription.create(data)


def update_subscription(gateway, donation, costum_price=None):
    subscription = gateway.subscription.find(donation.subscription_id)
    print(subscription)

    data = {
        # "payment_method_nonce": nonce,
        "plan_id": "djnd",
        "price": "%.2f" % (costum_price),
    }

    result = gateway.subscription.update(donation.subscription_id, data)
    print(vars(result))
    if result:
        if not result.subscription:
            return result
        donation.subscription_id = result.subscription.id
        donation.save()

    return result


def pay_bt_3d(
    gateway,
    nonce,
    amount,
    taxExempt=False,
    description="",
    campaign="DJND",
    merchant_account_id=None,
):
    data = {
        "amount": "%.2f" % (amount),
        "payment_method_nonce": nonce,
        "tax_exempt": taxExempt,
        "options": {
            "submit_for_settlement": True,
        },
        "custom_fields": {
            "campaign": campaign,
        },
    }
    if merchant_account_id:
        data.update(merchant_account_id=merchant_account_id)
    result = gateway.transaction.sale(data)
    print(result)
    return result


def get_hook(gateway, signature, payload):
    webhook_notification = gateway.webhook_notification.parse(signature, payload)
    return webhook_notification


def cancel_subscription(gateway, subscription_id):
    return gateway.subscription.cancel(subscription_id)


def get_gateway_from_campaign(campaign):
    if braintree_credentials := campaign.braintree_api:
        return _build_gateway(braintree_credentials)
    raise Exception("No braintree credentials found for campaign")


def get_gateway_from_model(braintree_api):
    return _build_gateway(braintree_api)


def get_public_keys_from_signature(signature):
    return [part.split("|", 1)[0] for part in signature.split("&") if "|" in part]
