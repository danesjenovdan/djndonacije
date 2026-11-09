import slack
import zulip
from django.conf import settings

if settings.SLACK_KEY:
    sc = slack.WebClient(settings.SLACK_KEY, timeout=30)

if settings.ZULIP_API_KEY and settings.ZULIP_EMAIL and settings.ZULIP_SITE:
    zc = zulip.Client(
        config_file=None,
        site=settings.ZULIP_SITE,
        api_key=settings.ZULIP_API_KEY,
        email=settings.ZULIP_EMAIL,
    )


def send_slack_msg(message, channel):
    if settings.SLACK_KEY:
        try:
            sc.api_call("chat.postMessage", json={"channel": channel, "text": message})
        except Exception as e:
            # TODO send sentry error
            print(e)


def send_zulip_msg(message, channel, topic):
    if settings.ZULIP_API_KEY and settings.ZULIP_EMAIL and settings.ZULIP_SITE:
        try:
            zc.send_message(
                {
                    "type": "channel",
                    "to": channel,
                    "topic": topic,
                    "content": message,
                }
            )
        except Exception as e:
            # TODO send sentry error
            print(e)
