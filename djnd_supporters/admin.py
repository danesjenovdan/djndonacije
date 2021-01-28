from django.contrib import admin
from djnd_supporters.models import Gift, Donation, DonationCampaign, RecurringDonation
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class DonationResource(resources.ModelResource):

    class Meta:
        model = Donation


class RecurringDonationResource(resources.ModelResource):

    class Meta:
        model = RecurringDonation


class DonationAdmin(ImportExportModelAdmin):
    readonly_fields = ('address',)
    list_display = ('amount', 'subscriberName', 'address', 'is_paid', 'created', 'payment_method', 'campaign')
    list_filter = ('amount', 'campaign', 'is_paid')
    resource_class = DonationResource

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
