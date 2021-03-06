import braintree
from django.conf import settings
from datetime import date, timedelta

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Production,
        merchant_id=settings.MERCHANT_ID,
        public_key=settings.PUBLIC_KEY,
        private_key=settings.PRIVATE_KEY
    )
)

def client_token(user=None):
    if not user:
        return gateway.client_token.generate()
    if user.braintree_id:
        customer_id = user.braintree_id
    else:
        print({
            'first_name': user.name,
            'last_name': user.surname,
            'company': '',
            'email': user.email,
            #'phone': '',
            #'fax': '',
            #'website': ''
        })
        result = gateway.customer.create({
            'first_name': user.name,
            'last_name': user.surname,
            #'company': '',
            'email': user.email,
            #'phone': '',
            #'fax': '',
            #'website': ''
        })
        if result.is_success:
            user.braintree_id = result.customer.id
            user.save()
            customer_id = result.customer.id

    return gateway.client_token.generate({
        'customer_id': customer_id
    })

def create_subscription(nonce, costum_price=None):
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

def pay_bt_3d(nonce, amount, taxExempt=False):
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
            'three_d_secure': {
                'required': True
            },
        }
    })
    print(result)
    return result

def get_hook(signature, payload):
    webhook_notification = gateway.webhook_notification.parse(signature, payload)
    return webhook_notification
