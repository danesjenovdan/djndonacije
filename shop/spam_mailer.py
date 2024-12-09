import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth


def send_mail_spam(subject, text_content, to_mail, html_content=None, file=None):
    if file:
        files = {"file": file}
    else:
        files = None
    requests.post(
        settings.MAILER_URL,
        data={
            "subject": subject,
            "text_content": text_content,
            "html_content": html_content,
            "to_mail": to_mail,
        },
        files=files,
        auth=HTTPBasicAuth(settings.MAILER_AUTH[0], settings.MAILER_AUTH[1]),
    )
