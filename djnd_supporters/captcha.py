import requests
from django.conf import settings
from sentry_sdk import capture_exception, capture_message


def validate_captcha(captcha_query):
    if not captcha_query or not isinstance(captcha_query, str) or ";" not in captcha_query:
        return False

    captcha_id, captcha_answer = captcha_query.split(";", maxsplit=1)
    if not captcha_id.isalnum() or not captcha_answer.isalnum():
        return False

    try:
        response = requests.post(
            f"{settings.CAPTCHA_BASE_URL}/validateCaptcha/{captcha_id}?captchaAnswer={captcha_answer}",
            timeout=10,
        )
        response.raise_for_status()
        response_json = response.json()
    except requests.exceptions.RequestException as e:
        capture_exception(e)
        return False

    if not isinstance(response_json, dict) or "responseCaptcha" not in response_json:
        capture_message(f"Invalid response from captcha api: {response_json}")
        return False

    return response_json["responseCaptcha"] == "success"
