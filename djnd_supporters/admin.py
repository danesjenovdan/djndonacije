from django.contrib import admin
from djnd_supporters.models import Transaction, DonationCampaign, Subscription, Subscriber
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class TransactionResource(resources.ModelResource):

    class Meta:
        model = Transaction


class SubscriptionResource(resources.ModelResource):

    class Meta:
        model = Subscription


class SubscriberResource(resources.ModelResource):

    class Meta:
        model = Subscriber


class TransactionInline(admin.TabularInline):
    readonly_fields = ['created']
    #fields = ['created', 'email_content']
    model = Transaction
    extra = 0


class SubscriptionInline(admin.TabularInline):
    readonly_fields = ['created']
    #fields = ['created', 'email_content']
    #search_fields = ['subscriber__token']
    model = Subscription
    extra = 0


class SubscriberAdmin(ImportExportModelAdmin):
    resource_class = SubscriberResource
    search_fields = ['token', 'mautic_id']

    inlines = (
        TransactionInline, SubscriptionInline
    )


class TransactionAdmin(ImportExportModelAdmin):
    readonly_fields = ('address',)
    list_display = ('amount', 'subscriberName', 'address', 'is_paid', 'created', 'payment_method', 'campaign')
    list_filter = ('amount', 'campaign', 'is_paid', 'payment_method')
    resource_class = TransactionResource
    search_fields = ['subscriber__token', 'transaction_id']

    def subscriberName(self, obj):
        if obj.subscriber:
            return obj.subscriber.name
        else:
            return ''

    def address(self, obj):
        if obj.subscriber:
            return obj.subscriber.address
        else:
            return ''


class SubscriptionAdmin(ImportExportModelAdmin):
    readonly_fields = ('address',)
    list_display = ('amount', 'subscriberName', 'address', 'created', 'campaign', 'subscription_id')
    list_filter = ('amount', 'campaign')
    resource_class = SubscriptionResource
    search_fields = ['subscriber__token', 'subscription_id']
    def subscriberName(self, obj):
        if obj.subscriber:
            return obj.subscriber.name
        else:
            return ''

    def address(self, obj):
        if obj.subscriber:
            return obj.subscriber.address
        else:
            return ''

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(DonationCampaign)
admin.site.register(Subscriber, SubscriberAdmin)
