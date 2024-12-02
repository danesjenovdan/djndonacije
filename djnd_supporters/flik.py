import requests
import hmac
import hashlib
import json
import base64
import arrow

from requests.auth import HTTPBasicAuth
from enum import Enum

from django.conf import settings


FLIK_INITIAL_URL = (
    f"https://gateway.bankart.si/api/v3/transaction/{settings.FLIK_API_KEY}/debit"
)


class Status(str, Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    ERROR = "ERROR"

    @classmethod
    def as_choices(cls):
        return [(tag.value, tag.name) for tag in cls]


class InitialResponse:
    def __init__(self, **kwargs):
        self.redirect_url = kwargs.get("redirectUrl")
        self.uuid = kwargs.get("uuid")
        self.purchase_id = kwargs.get("purchaseId")
        self.payment_method = kwargs.get("paymentMethod")
        self.extra_data = kwargs.get("extraData")
        self.returnType = kwargs.get("returnType")
        self.success = kwargs.get("success")


class PaymentResultResponse:
    def __init__(self, **kwargs):
        self.result = kwargs.get("result")
        self.uuid = kwargs.get("uuid")
        self.merchant_transaction_id = kwargs.get("merchantTransactionId")
        self.transaction_type = kwargs.get("transactionType")
        self.payment_method = kwargs.get("paymentMethod")
        self.amount = kwargs.get("amount")
        self.currency = kwargs.get("currency")
        self.extra_data = kwargs.get("extraData")


def initialize_payment(
    transaction_id,
    amount,
    description,
    shopper_locale,
    customer_ip,
    success_url,
    error_url,
    cancel_url,
    callback_url,
    phone_number=None,
):
    data = {
        "merchantTransactionId": str(transaction_id),
        "amount": amount,
        "currency": "EUR",
        "successUrl": success_url,
        "errorUrl": error_url,
        "cancelUrl": cancel_url,
        "callbackUrl": callback_url,
        "description": description,
        "customer": {"ipAddress": customer_ip},
        "language": shopper_locale,
    }

    if phone_number:
        data["extraData"] = {"alias": phone_number}

    utc = arrow.utcnow()
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Date": utc.format("ddd, DD MMM YYYY HH:mm:ss UTC"),
    }
    sha512_data = hashlib.sha512(json.dumps(data).encode("utf-8")).hexdigest()

    signiture_url = FLIK_INITIAL_URL.split("bankart.si")[1]
    sig_data = f"""POST
{sha512_data}
{headers['Content-Type']}
{headers['Date']}
{signiture_url}"""

    signiture = hmac.new(
        str.encode(settings.FLIK_SS),
        sig_data.encode("utf-8"),
        digestmod=hashlib.sha512,
    ).digest()
    signiture = base64.b64encode(signiture)

    headers["X-Signature"] = signiture
    response = requests.post(
        FLIK_INITIAL_URL,
        data=json.dumps(data),
        headers=headers,
        auth=HTTPBasicAuth(settings.FLIK_USERNAME, settings.FLIK_PASSWORD),
    )
    if response.status_code != 200:
        return None
    else:
        return InitialResponse(**response.json())


def get_payment_result(data):
    return PaymentResultResponse(**data)
