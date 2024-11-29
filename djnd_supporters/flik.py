import requests
import hmac
import hashlib
import json
import base64
import arrow

from requests.auth import HTTPBasicAuth
from enum import Enum

from django.conf import settings
from django.utils.translation import gettext_lazy as _

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


def initialize_payment(
    transaction_id,
    amount,
    description,
    customer_ip,
    success_url,
    error_url,
    cancel_url,
    callback_url,
    shopper_locale="sl",
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

    response_data = response.json()

    if response_data.get("success"):
        return {
            "redirect_url": response_data["redirectUrl"],
            "uuid": response_data["uuid"],
        }
    else:
        return None
