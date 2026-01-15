import os.path
from enum import Enum
from io import BytesIO
from secrets import token_hex

from behaviors.behaviors import Published, Timestamped
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.validators import URLValidator
from django.db import models
from PIL import Image as PILImage

from djnd_supporters.mautic_api import MauticApi

# Create your models here.

mautic_api = MauticApi()


class DonationType(Enum):
    PARLAMETER_SI = "PARLAMETER_SI"
    PARLAMETER_HR = "PARLAMETER_HR"
    PARLAMETER_BA = "PARLAMETER_BA"
    DJND = "DJND"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class OptionalSchemeURLValidator(URLValidator):
    def __call__(self, value):
        if "://" not in value:
            # Validate as if it were http://
            value = "http://" + value
        super(OptionalSchemeURLValidator, self).__call__(value)


class Subscriber(User, Timestamped):
    token = models.TextField(blank=False, null=False, default="")
    name = models.CharField(default="Anonimnež_ica", max_length=128)
    mautic_id = models.IntegerField(null=True, blank=True, unique=True)
    address = models.TextField(null=True, blank=True)
    customer_id = models.TextField(
        null=True, blank=True, help_text="Braintree customer id"
    )

    def save(self, *args, **kwargs):
        if not self.pk and not self.token:
            self.token = token_hex(16)
            self.username = self.token
        super(Subscriber, self).save(*args, **kwargs)

    def save_to_mautic(self, email):
        response, response_status = mautic_api.createContact(
            email=email, name=self.name if self.name else "", token=self.token
        )
        if response_status == 200:
            self.mautic_id = response["contact"]["id"]
            self.save()
            return self, 200
        else:
            return response, response_status

    def update_contact(self, data):
        response, response_status = mautic_api.patchContact(
            id=self.mautic_id, data=data
        )
        return response, response_status

    def __str__(self):
        return "Subscriber_" + str(self.name)


class Transaction(Timestamped):
    subscriber = models.ForeignKey(
        "Subscriber",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    nonce = models.TextField(null=True, blank=True)
    amount = models.DecimalField(default=0.0, decimal_places=1, max_digits=20)
    is_paid = models.BooleanField(default=True)
    payment_method = models.CharField(max_length=50, default="braintree")
    reference = models.CharField(max_length=50, null=True, blank=True)
    campaign = models.ForeignKey(
        "DonationCampaign",
        related_name="donations",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    transaction_id = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return (
            (self.subscriber.name if self.subscriber else "?")
            + " -> "
            + str(self.amount)
        )

    def get_amount(self):
        try:
            amount = self.__getattribute__("recurringdonation").amount * 12
        except:
            amount = self.amount
        return amount


class Subscription(Timestamped):
    subscriber = models.ForeignKey(
        "Subscriber",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscriptions",
    )
    token = models.TextField(null=True, blank=True)
    amount = models.DecimalField(default=0.0, decimal_places=1, max_digits=20)
    subscription_id = models.CharField(max_length=128, null=True, blank=True)
    campaign = models.ForeignKey(
        "DonationCampaign",
        related_name="subscriptions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return (
            (self.subscriber.name if self.subscriber else "?")
            + " -> "
            + str(self.amount)
        )


class Image(Timestamped):
    donation = models.OneToOneField("Transaction", on_delete=models.CASCADE)
    token = models.TextField(blank=False, null=False, default="1234567890")
    image = models.ImageField(upload_to="images")
    url = models.CharField(
        max_length=200, null=True, blank=True, validators=[OptionalSchemeURLValidator()]
    )
    thumbnail = models.ImageField(upload_to="thumbs")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.token = token_hex(16)

        if self.image:
            if not self.make_thumbnail():
                # set to a default thumbnail
                raise Exception("Could not create thumbnail - is the file type valid?")
        if self.url:
            if "://" not in self.url:
                self.url = "https://" + self.url

        super(Image, self).save(*args, **kwargs)

    def get_upload_url(self):
        return settings.UPLOAD_IMAGE_URL + self.token

    def make_thumbnail(self):

        image = PILImage.open(self.image)
        image.thumbnail(settings.THUMB_SIZE, PILImage.ANTIALIAS)

        thumb_name, thumb_extension = os.path.splitext(self.image.name)
        thumb_extension = thumb_extension.lower()

        thumb_filename = thumb_name + "_thumb" + thumb_extension

        if thumb_extension in [".jpg", ".jpeg"]:
            FTYPE = "JPEG"
        elif thumb_extension == ".gif":
            FTYPE = "GIF"
        elif thumb_extension == ".png":
            FTYPE = "PNG"
        else:
            return False  # Unrecognized file type

        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        # set save=False, otherwise it will run in an infinite loop
        self.thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()

        return True


class DonationCampaign(Timestamped):
    name = models.CharField(max_length=128, verbose_name="Ime donacijske kampanje")
    slug = models.CharField(
        max_length=32,
        verbose_name="Slug",
        help_text="Male črke, brez presledkov (primer: danes-je-nov-dan). Je sestavni del URL-ja na frontendu za novičnike in donacije (npr. moj.djnd.si/danes-je-nov-dan/doniraj)",
    )
    title = models.CharField(
        null=True,
        blank=True,
        max_length=256,
        verbose_name="Naslov",
        help_text="Prikaže se na https://moj.djnd.si/&lt;slug&gt;/doniraj",
    )
    title_en = models.CharField(
        null=True,
        blank=True,
        max_length=256,
        verbose_name="Naslov (angleščina)",
        help_text="Prikaže se na https://moj.djnd.si/&lt;slug&gt;/doniraj",
    )
    subtitle = models.TextField(
        null=True,
        blank=True,
        verbose_name="Podnaslov",
        help_text="Prikaže se na https://moj.djnd.si/&lt;slug&gt;/doniraj",
    )
    subtitle_en = models.TextField(
        null=True,
        blank=True,
        verbose_name="Podnaslov (angleščina)",
        help_text="Prikaže se na https://moj.djnd.si/&lt;slug&gt;/doniraj",
    )
    upn_name = models.CharField(
        null=True,
        blank=True,
        max_length=32,
        verbose_name="UPN namen na plačilnem nalogu",
        default="Donacija",
    )
    has_upn = models.BooleanField(default=True, verbose_name="Sprejemamo UPN donacije?")
    has_flik = models.BooleanField(
        default=False, verbose_name="Sprejemamo flik donacije?"
    )
    has_braintree = models.BooleanField(
        default=True, verbose_name="Sprejemamo braintree enkratne donacije?"
    )
    has_braintree_subscription = models.BooleanField(
        default=True, verbose_name="Sprejemamo braintree mesečne donacije?"
    )
    upn_email_template = models.IntegerField(
        null=True, blank=True, verbose_name="Mautic email ID za UPN donacijo"
    )
    onetime_donation_email_template = models.IntegerField(
        null=True, blank=True, verbose_name="Mautic email ID za enkratno donacijo"
    )
    bt_subscription_email_template = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Mautic email ID za braintree mesečno donacijo (prvi email)",
    )
    has_upload_image = models.BooleanField(
        default=False, help_text="Has donation uploading image"
    )
    web_hook_url = models.TextField(
        help_text="Web hook for subscription events", null=True, blank=True
    )
    braintee_subscription_plan_id = models.CharField(
        max_length=32,
        verbose_name="Braintree subscription plan id",
        null=True,
        blank=True,
    )
    slack_report_channel = models.TextField(
        blank=False,
        null=False,
        default="#djnd-bot",
        help_text="Slack channel for events reporting. Starts with #",
    )
    charged_unsuccessfully_email = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Mautic email ID za neuspešno obračunano braintree mesečno donacijo",
    )
    subscription_canceled_email = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Mautic email ID za preklic braintree mesečnih donacij",
    )
    subscription_charged_successfully = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Mautic email ID za uspešno obračunano braintree mesečno donacijo",
    )
    segment = models.IntegerField(
        null=True, blank=True, verbose_name="Mautic segment ID"
    )
    welcome_email_tempalte = models.IntegerField(
        null=True, blank=True, verbose_name="Mautic email ID za welcome mail"
    )
    edit_subscriptions_email_tempalte = models.IntegerField(
        null=True, blank=True, verbose_name="Mautic email ID za urejanje naročnine"
    )
    redirect_url = models.URLField(
        null=True, blank=True, help_text="Redirect url on success"
    )
    css_file = models.FileField(upload_to="css", null=True, blank=True)
    braintree_merchant_account_id = models.CharField(
        null=True,
        blank=True,
        max_length=128,
        help_text="ID of braintree merchant account.",
    )
    add_to_newsletter_confirmation_required = models.BooleanField(
        default=False, verbose_name="Prijava na novičnik zahteva potrditev"
    )

    def __str__(self):
        return self.name


class PredefinedAmount(Timestamped):
    donation_campaign = models.ForeignKey(
        "DonationCampaign", related_name="amounts", on_delete=models.CASCADE
    )
    amount = models.IntegerField()
    one_time_amount = models.BooleanField(
        default=True, help_text="Enable amount for one time donation"
    )
    recurring_amount = models.BooleanField(
        default=True, help_text="Enable amount for recurring donation"
    )
