import slack
from django.conf import settings

sc = slack.WebClient(settings.SLACK_KEY, timeout=30)


def send_slack_msg(message, channel):
    try:
        sc.api_call("chat.postMessage", json={"channel": channel, "text": message})
    except Exception as e:
        # TODO send sentry error
        print(e)
