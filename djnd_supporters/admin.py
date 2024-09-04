from django.contrib import admin
from djnd_supporters.models import Transaction, DonationCampaign, Subscription, Subscriber, VerificationQuestion, PredefinedAmount
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


class AmountInlineAdmin(admin.TabularInline):
    readonly_fields = ['created', 'modified']
    model = PredefinedAmount
    extra = 0


class DonationCampaignAdmin(admin.ModelAdmin):
    inlines = [AmountInlineAdmin]
    readonly_fields = ['mautic_manage_subscription_url', 'mautic_confirm_subscription_url']
    search_fields = ['name', 'slug']
    fieldsets = [
        (
            None,
            {
                "fields": ["name", "slug"],
            },
        ),
        (
            "Novičnik",
            {
                "fields": ["segment", "edit_subscriptions_email_tempalte", "mautic_manage_subscription_url", "welcome_email_tempalte", "mautic_confirm_subscription_url", "add_to_newsletter_confirmation_required"],
            },
        ),
        (
            "Nastavitve za frontend [https://moj.djnd.si/]",
            {
                "fields": ["title", "subtitle", "css_file", "css_file_url"], # "redirect_url", "has_upload_image", 
            },
        ),
        (
            "Donacije",
            {
                "fields": ["slack_report_channel",
                           "has_upn",
                           "upn_name",
                           "upn_email_template",
                           "has_braintree",
                           "bt_email_template",
                           "has_braintree_subscription",
                           "bt_subscription_email_template",
                           "subscription_charged_successfully",
                           "charged_unsuccessfully_email",
                           "subscription_canceled_email", 
                           "braintee_subscription_plan_id",
                           "web_hook_url",
                           "braintree_merchant_account_id"],
            },
        ),
    ]

    def mautic_manage_subscription_url(self, obj):
        return f"http://moj.djnd.si/{obj.slug}/urejanje-narocnine?token={{contactfield=token}}&email={{contactfield=email}}"
    
    def mautic_confirm_subscription_url(self, obj):
        if obj.add_to_newsletter_confirmation_required:
            return f"http://moj.djnd.si/{obj.slug}/prijava-uspesna?segment_id={obj.segment}&token={{contactfield=token}}&email={{contactfield=email}}"
        else:
            return "/"

class TransactionAdmin(ImportExportModelAdmin):
    readonly_fields = ('address',)
    list_display = ('amount', 'subscriberName', 'address', 'is_paid', 'created', 'payment_method', 'campaign')
    list_filter = ('amount', 'campaign', 'is_paid', 'payment_method')
    resource_class = TransactionResource
    search_fields = ['subscriber__token', 'transaction_id']
    autocomplete_fields = ['subscriber', 'campaign']

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
    list_display = ('amount', 'subscriberName', 'address', 'created', 'campaign', 'subscription_id', 'is_active')
    list_filter = ('amount', 'campaign')
    resource_class = SubscriptionResource
    search_fields = ['subscriber__token', 'subscription_id']
    autocomplete_fields = ['subscriber', 'campaign']

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


class VerificationQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answer' )

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(DonationCampaign, DonationCampaignAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(VerificationQuestion, VerificationQuestionAdmin)
