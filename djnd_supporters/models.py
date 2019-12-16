from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.validators import URLValidator

from django.conf import settings

from secrets import token_hex
from behaviors.behaviors import Timestamped, Published

from djnd_supporters import mautic_api

import os.path
from PIL import Image as PILImage
from io import BytesIO
# Create your models here.


class OptionalSchemeURLValidator(URLValidator):
    def __call__(self, value):
        if '://' not in value:
            # Validate as if it were http://
            value = 'http://' + value
        super(OptionalSchemeURLValidator, self).__call__(value)


class Subscriber(User, Timestamped):
    token = models.TextField(blank=False, null=False, default='1234567890')
    name = models.CharField(default="Anonimnež_ica", max_length=128)
    mautic_id = models.IntegerField(null=True, blank=True, unique=True)
    address = models.TextField(null=True, blank=True)
    #email = models.EmailField()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.token = token_hex(16)
            self.username = self.token
        super(Subscriber, self).save(*args, **kwargs)

    def save_to_mautic(self, email, send_email=True):
        response, response_status = mautic_api.createContact(email=email, name=self.name, token=self.token)
        if response_status == 200:
            self.mautic_id = response['contact']['id']
            self.save()
            if send_email:
                response, response_status = mautic_api.sendEmail(
                    settings.MAIL_TEMPLATES['WELLCOME_MAIL'],
                    response['contact']['id'],
                    {
                        'unsubscribe_text': 'asdasd'
                    }
                )
            return self, 200
        else:
            return response, response_status

    def __str__(self):
        return "Subscriber_" + str(self.name)


class Donation(Timestamped):
    subscriber = models.ForeignKey(
        'Subscriber',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    nonce = models.TextField(null=True, blank=True)
    amount = models.DecimalField(default=0.0, decimal_places=1, max_digits=20)
    # is_assigned is helper atrribut using for group donations.
    is_assigned = models.BooleanField(default=True)


class Image(Timestamped):
    donation = models.OneToOneField('Donation', on_delete=models.CASCADE)
    token = models.TextField(blank=False, null=False, default='1234567890')
    image = models.ImageField(upload_to='images')
    url = models.CharField(max_length=200, null=True, blank=True, validators=[OptionalSchemeURLValidator()])
    thumbnail = models.ImageField(upload_to='thumbs')

    def save(self, *args, **kwargs):
        if not self.pk:
            self.token = token_hex(16)

        if self.image:
            if not self.make_thumbnail():
                # set to a default thumbnail
                raise Exception('Could not create thumbnail - is the file type valid?')
        if self.url:
            if '://' not in self.url:
                self.url = 'https://' + self.url

        super(Image, self).save(*args, **kwargs)

    def get_upload_url(self):
        return settings.UPLOAD_IMAGE_URL + self.token

    def make_thumbnail(self):

        image = PILImage.open(self.image)
        image.thumbnail(settings.THUMB_SIZE, PILImage.ANTIALIAS)

        thumb_name, thumb_extension = os.path.splitext(self.image.name)
        thumb_extension = thumb_extension.lower()

        thumb_filename = thumb_name + '_thumb' + thumb_extension

        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.gif':
            FTYPE = 'GIF'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return False    # Unrecognized file type

        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        # set save=False, otherwise it will run in an infinite loop
        self.thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()

        return True


class Gift(Timestamped):
    subscriber = models.ForeignKey(
        'Subscriber',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gifts'
    )
    nonce = models.TextField(null=True, blank=True)
    amount = models.DecimalField(default=0.0, decimal_places=1, max_digits=20)
    gifts = models.ManyToManyField('Donation', related_name='gifts')
