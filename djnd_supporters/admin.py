from django.contrib import admin
from djnd_supporters.models import Gift, Donation, DonationCampaign, RecurringDonation, Subscriber
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class DonationResource(resources.ModelResource):

    class Meta:
        model = Donation


class RecurringDonationResource(resources.ModelResource):

    class Meta:
        model = RecurringDonation


class SubscriberResource(resources.ModelResource):

    class Meta:
        model = Subscriber


class DonationInline(admin.TabularInline):
    readonly_fields = ['created']
    #fields = ['created', 'email_content']
    model = Donation
    extra = 0


class RecurringDonationInline(admin.TabularInline):
    readonly_fields = ['created']
    #fields = ['created', 'email_content']
    #search_fields = ['subscriber__token']
    model = RecurringDonation
    extra = 0


class SubscriberAdmin(ImportExportModelAdmin):
    resource_class = SubscriberResource
    search_fields = ['token', 'mautic_id']

    inlines = (
        DonationInline, RecurringDonationInline
    )


class DonationAdmin(ImportExportModelAdmin):
    readonly_fields = ('address',)
    list_display = ('amount', 'subscriberName', 'address', 'is_paid', 'created', 'payment_method', 'campaign')
    list_filter = ('amount', 'campaign', 'is_paid', 'payment_method')
    resource_class = DonationResource
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


class RecurringDonationAdmin(ImportExportModelAdmin):
    readonly_fields = ('address',)
    list_display = ('amount', 'subscriberName', 'address', 'is_paid', 'created', 'payment_method', 'campaign')
    list_filter = ('amount', 'campaign', 'is_paid')
    resource_class = RecurringDonationResource
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

admin.site.register(Donation, DonationAdmin)
admin.site.register(RecurringDonation, RecurringDonationAdmin)
admin.site.register(Gift)
admin.site.register(DonationCampaign)
admin.site.register(Subscriber, SubscriberAdmin)
