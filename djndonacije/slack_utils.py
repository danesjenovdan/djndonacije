import slack
from django.conf import settings

if settings.SLACK_KEY:
    sc = slack.WebClient(settings.SLACK_KEY, timeout=30)


def send_slack_msg(message, channel):
    if settings.SLACK_KEY:
        try:
            sc.api_call("chat.postMessage", json={"channel": channel, "text": message})
        except Exception as e:
            # TODO send sentry error
            print(e)
