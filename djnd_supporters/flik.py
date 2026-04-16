import base64
import hashlib
import hmac
import json
from enum import Enum

import arrow
import requests
from requests.auth import HTTPBasicAuth


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
        self.return_type = kwargs.get("returnType")
        self.success = kwargs.get("success")


class PaymentResponse:
    def __init__(self, **kwargs):
        self.result = kwargs.get("result")
        self.uuid = kwargs.get("uuid")
        self.merchant_transaction_id = kwargs.get("merchantTransactionId")
        self.purchase_id = kwargs.get("purchaseId")
        self.transaction_type = kwargs.get("transactionType")
        self.payment_method = kwargs.get("paymentMethod")
        self.amount = kwargs.get("amount")
        self.currency = kwargs.get("currency")
        self.customer = kwargs.get("customer")
        self.extra_data = kwargs.get("extraData")


class PaymentSuccessResponse(PaymentResponse):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status = "success"


class PaymentRefundResponse(PaymentResponse):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status = "refund"
        self.message = kwargs.get("message")
        self.code = kwargs.get("code")
        self.adapter_message = kwargs.get("adapterMessage")
        self.adapter_code = kwargs.get("adapterCode")


class PaymentErrorResponse(PaymentResponse):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status = "error"
        self.message = kwargs.get("message")
        self.code = kwargs.get("code")
        self.adapter_message = kwargs.get("adapterMessage")
        self.adapter_code = kwargs.get("adapterCode")


class FlikAuth:
    def __init__(self, api_key, shared_secret, username, password):
        self.api_key = api_key
        self.shared_secret = shared_secret
        self.username = username
        self.password = password
        self.initial_url = (
            f"https://gateway.bankart.si/api/v3/transaction/{api_key}/debit"
        )
        self.signiture_url = f"/api/v3/transaction/{api_key}/debit"


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
    flik_auth: FlikAuth,
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

    sig_data = f"""POST
{sha512_data}
{headers['Content-Type']}
{headers['Date']}
{flik_auth.signiture_url}"""

    signiture = hmac.new(
        str.encode(flik_auth.shared_secret),
        sig_data.encode("utf-8"),
        digestmod=hashlib.sha512,
    ).digest()
    signiture = base64.b64encode(signiture)

    headers["X-Signature"] = signiture
    response = requests.post(
        flik_auth.initial_url,
        data=json.dumps(data),
        headers=headers,
        auth=HTTPBasicAuth(flik_auth.username, flik_auth.password),
    )
    if response.status_code != 200:
        print(f"Failed to initialize payment: {response.text}")
        return None
    else:
        return InitialResponse(**response.json())


def get_payment_result(data):
    if data["transactionType"] == "REFUND":
        return PaymentRefundResponse(**data)
    elif data["result"] == "OK":
        if data["transactionType"] == "DEBIT":
            return PaymentSuccessResponse(**data)
    elif data["result"] == "ERROR":
        return PaymentErrorResponse(**data)
    raise NotImplementedError("Unknown transaction type")
