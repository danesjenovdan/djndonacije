import braintree
from django.conf import settings
from datetime import date, timedelta

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=settings.MERCHANT_ID,
        public_key=settings.PUBLIC_KEY,
        private_key=settings.PRIVATE_KEY
    )
)

def client_token(user):
    if user.braintree_id:
        customer_id = user.braintree_id
    else:
        print({
            'first_name': user.name,
            'last_name': user.surename,
            'company': '',
            'email': user.email,
            #'phone': '',
            #'fax': '',
            #'website': ''
        })
        result = gateway.customer.create({
            'first_name': user.name,
            'last_name': user.surename,
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

def create_subscription(nonce, user, costum_price=None):
    data = {
        'payment_method_nonce': nonce,
        'plan_id': 'djnd',
    }

    if costum_price:
        data.update({'price': costum_price})

    result = gateway.subscription.create(data)

    if result:
        if not result.subscription:
            return result
        user.subscription_id = result.subscription.id
        user.save()
    return result

def update_subscription(user, costum_price=None):
    subscription = gateway.subscription.find(user.subscription_id)
    old_plan_id = subscription.plan_id
    print(subscription)

    data = {
        #"payment_method_nonce": nonce,
        "plan_id": PLAN,
        "price": '%.2f' % (costum_price * settings.VAT),
        "options": {"prorate_charges": True}
    }

    result = gateway.subscription.update(user.subscription_id, data)
    print(vars(result))
    if result:
        if not result.subscription:
            return result
        user.subscription_id = result.subscription.id
        user.is_active_guy = True
        user.save()

    return result

def pay_bt_3d(user, amount, nonce):
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
        'amount': str(amount),
        'payment_method_nonce': nonce,
        'options': {
            'submit_for_settlement': True,
            'three_d_secure': {
                'required': True
            },
        }
    })
    print(result)
    return result