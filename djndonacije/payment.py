import braintree
from django.conf import settings
from datetime import date, timedelta

gateway = settings.GATEWAY

def client_token(user=None):
    if not user:
        # create empty user
        result = gateway.customer.create({})
        return {
            'token': gateway.client_token.generate(
                {
                    'customer_id': result.customer.id
                }),
            'customer_id': result.customer.id
        }
    if user.braintree_id:
        customer_id = user.braintree_id
    else:
        # create empty user
        result = gateway.customer.create({})
        if result.is_success:
            user.braintree_id = result.customer.id
            user.save()
            customer_id = result.customer.id
    return {
            'token': gateway.client_token.generate(
                {
                    'customer_id': customer_id
                }),
            'customer_id': customer_id
        }

# def create_subscription(nonce, user, costum_price=None):
#     data = {
#         'payment_method_nonce': nonce,
#         'plan_id': 'djnd',
#     }

#     if costum_price:
#         data.update({'price': costum_price})

#     result = gateway.subscription.create(data)

#     if result:
#         if not result.subscription:
#             return result
#         user.subscription_id = result.subscription.id
#         user.save()
#     return result

# def update_subscription(user, costum_price=None):
#     subscription = gateway.subscription.find(user.subscription_id)
#     old_plan_id = subscription.plan_id
#     print(subscription)

#     data = {
#         #"payment_method_nonce": nonce,
#         "plan_id": 'djnd',
#         "price": '%.2f' % (costum_price),
#         "options": {"prorate_charges": True}
#     }

#     result = gateway.subscription.update(user.subscription_id, data)
#     print(vars(result))
#     if result:
#         if not result.subscription:
#             return result
#         user.subscription_id = result.subscription.id
#         user.is_active_guy = True
#         user.save()

#     return result

def create_subscription(nonce, customer_id, costum_price=None):
    #result = gateway.payment_method.create({
    #    "customer_id": customer_id,
    #    "payment_method_nonce": nonce
    #})

    #print(vars(result))

    data = {
        'payment_method_nonce': nonce,
        'plan_id': 'djnd',
    }

    if costum_price:
        print(costum_price)
        data.update({'price': '%.2f' % (costum_price),})

    print(data)
    return gateway.subscription.create(data)

def update_subscription(donation, costum_price=None):
    subscription = gateway.subscription.find(donation.subscription_id)
    print(subscription)

    data = {
        #"payment_method_nonce": nonce,
        "plan_id": 'djnd',
        "price": '%.2f' % (costum_price),
    }

    result = gateway.subscription.update(donation.subscription_id, data)
    print(vars(result))
    if result:
        if not result.subscription:
            return result
        donation.subscription_id = result.subscription.id
        donation.save()

    return result

def pay_bt_3d(nonce, amount, taxExempt=False, description='', campaign='DJND'):
    print({
        'amount': str(amount),
        'payment_method_nonce': nonce,
        'options': {
            'submit_for_settlement': True,
            'three_d_secure': {
                'required': True
            },
        }
    })
    result = gateway.transaction.sale({
        'amount': '%.2f' % (amount),
        'payment_method_nonce': nonce,
        'tax_exempt': taxExempt,
        'options': {
            'submit_for_settlement': True,
        },
        "custom_fields": {
            "campaign": campaign,
        },
    })
    print(result)
    return result

def get_hook(signature, payload):
    webhook_notification = gateway.webhook_notification.parse(signature, payload)
    return webhook_notification


def cancel_subscription(subscription_id):
    return gateway.subscription.cancel(subscription_id)
