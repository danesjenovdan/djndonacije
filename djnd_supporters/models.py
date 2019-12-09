from django.db import models
from django.contrib.auth.models import User

from secrets import token_hex
from behaviors.behaviors import Timestamped, Published

from djnd_supporters import mautic_api

# Create your models here.

class Subscriber(User, Timestamped):
    token = models.TextField(blank=False, null=False, default='1234567890')
    name = models.CharField(default="Anonimnež_ica", max_length=128)
    subscription_id = models.CharField(max_length=128, null=True, blank=True)
    mautic_id = models.IntegerField(null=True, blank=True, unique=True)
    #email = models.EmailField()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.token = token_hex(16)
            self.username = self.token
        super(Subscriber, self).save(*args, **kwargs)

    def get_child(self):
        if Supporter.objects.filter(subscriber_ptr=self.id):
            return Supporter.objects.get(subscriber_ptr=self.id)
        elif Gift.objects.filter(subscriber_ptr=self.id):
            return Gift.objects.get(subscriber_ptr=self.id)
    
    def save_to_mautic(self, email, send_email=True):
        response = mautic_api.createContact(email=email, name=self.name, token=self.token)
        self.mautic_id = response['contact']['id']
        self.save()
        if send_email:
            mautic_api.sendEmail(
                2, # 2 is wellcome mail
                response['contact']['id'],
                {
                    'unsubscribe_text': 'asdasd'
                }
            )
        return self

    @property
    def model_type(self):
        if Supporter.objects.filter(subscriber_ptr=self.id):
            return 'supporter'
        elif Gift.objects.filter(subscriber_ptr=self.id):
            return 'gift'

    @property
    def donation_amount(self):
        return sum(self.donations.values_list('amount', flat=True))
    
    def __str__(self):
        return "Subscriber_" + str(self.name)


## this is workaround beacuse Supporter cannot overide email field if email is not member of non abstract model
#class Subscriber(AbstractSubscriber):
#    pass


class Supporter(Subscriber):
    # subsriber info
    #email = models.EmailField(unique=True)
    surname = models.CharField(max_length=128)
    # mautic_id = models.IntegerField(null=True, blank=True, unique=True)

    newsletter = models.BooleanField(default=False)
    is_supporter = models.BooleanField(default=False)

    #batched = models.BooleanField(default=False) #??

    # payment fields
    braintree_id = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return "Supporter_" + str(self.email)

    class Meta:
        verbose_name = 'Supporter'
        verbose_name_plural = 'Supporters'


class Gift(Subscriber):
    sender = models.ForeignKey(Supporter, related_name='gifts', on_delete=models.SET_NULL, null=True)
    send_at = models.DateField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    mail_content = models.TextField(default='')

    def __str__(self):
        return "Gift_" + str(self.email)

    #def save(self, *args, **kwargs):
    #    if not self.pk:
    #        self.token = token_hex(16)
    #    super(Subscriber, self).save(*args, **kwargs)

    def save_to_mautic(self, send_email_to_sender=True):
        response = mautic_api.createContact(self.email, self.token, self.name, '')
        self.mautic_id = response['contact']['id']
        self.save()
        if send_email_to_sender:
            mautic_api.sendEmail(
                4, # 4 is you send a gift mail
                self.sender.mautic_id,
                {}
            )
        return self

    def send_gift(self):
        mautic_api.sendEmail(
            3, # this is gift email
            self.mautic_id,
            {
                "tokens": {
                    "{email_content}": self.mail_content
                }
            }
        )
        mautic_api.sendEmail(
            5, # 5 is notification that we sent a gift
            self.sender.mautic_id,
            {}
        )
        self.sent = True
        self.save()

    class Meta:
        verbose_name = 'Gift'
        verbose_name_plural = 'Gifts'


class Milestone(Timestamped):
    name = models.CharField(max_length=512)
    budget = models.IntegerField()
    my_order = models.PositiveIntegerField(default=0, blank=False, null=False)
    on_project = models.ForeignKey('Project', related_name='milestones', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta(object):
        ordering = ['my_order']

class Project(Timestamped):
    name = models.CharField(max_length=512)
    description = models.TextField(default='')
    collected_funds = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def update_collected_funds(self):
        donations = self.donations.all().exclude(subscriber__subscription_id=None)
        self.collected_funds = sum(donations.values_list('amount', flat=True))
        self.save()

    @classmethod
    def update_all_funds(cls):
        for proj in cls.objects.all():
            proj.update_collected_funds()




class Donation(Timestamped):
    subscriber = models.ForeignKey('Subscriber', related_name='donations', on_delete=models.CASCADE)
    project = models.ForeignKey('Project', related_name='donations', on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
