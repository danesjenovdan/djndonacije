from django.contrib import admin
from djnd_supporters.models import Gift, Donation, DonationCampaign

class DonationAdmin(admin.ModelAdmin):
    readonly_fields = ('address',)
    list_display = ('amount', 'subscriberName', 'address', 'created', 'payment_method', 'campaign')
    list_filter = ('amount', 'campaign')

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
admin.site.register(Gift)
admin.site.register(DonationCampaign)
