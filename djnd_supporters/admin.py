from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from djnd_supporters.models import (
    DonationCampaign,
    PredefinedAmount,
    Subscriber,
    Subscription,
    Transaction,
)


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
    readonly_fields = ["created"]
    # fields = ['created', 'email_content']
    model = Transaction
    extra = 0


class SubscriptionInline(admin.TabularInline):
    readonly_fields = ["created"]
    # fields = ['created', 'email_content']
    # search_fields = ['subscriber__token']
    model = Subscription
    extra = 0


class SubscriberAdmin(ImportExportModelAdmin):
    readonly_fields = ["token", "mautic_id"]
    resource_class = SubscriberResource
    search_fields = ["token", "mautic_id"]

    inlines = (TransactionInline, SubscriptionInline)


class AmountInlineAdmin(admin.TabularInline):
    readonly_fields = ["created", "modified"]
    model = PredefinedAmount
    extra = 0


class DonationCampaignAdmin(admin.ModelAdmin):
    inlines = [AmountInlineAdmin]
    readonly_fields = [
        "mautic_manage_subscription_url",
        "mautic_confirm_subscription_url",
    ]
    search_fields = ["name", "slug"]
    fieldsets = [
        (
            None,
            {
                "fields": ["name"],
            },
        ),
        (
            "Novičnik",
            {
                "fields": [
                    "segment",
                    "welcome_email_tempalte",
                    "add_to_newsletter_confirmation_required",
                    "mautic_confirm_subscription_url",
                    "edit_subscriptions_email_tempalte",
                    "mautic_manage_subscription_url",
                ],
            },
        ),
        (
            "Donacije",
            {
                "fields": [
                    "slack_report_channel",
                    "has_upn",
                    "upn_name",
                    "upn_email_template",
                    "has_flik",
                    "has_braintree",
                    "onetime_donation_email_template",
                    "has_braintree_subscription",
                    "bt_subscription_email_template",
                    "subscription_charged_successfully",
                    "charged_unsuccessfully_email",
                    "subscription_canceled_email",
                    "braintee_subscription_plan_id",
                    "web_hook_url",
                    "braintree_merchant_account_id",
                ],
            },
        ),
        (
            "Nastavitve za frontend [https://moj.djnd.si/]",
            {
                "fields": [
                    "slug",
                    "title",
                    "subtitle",
                    "css_file",
                ],  # "redirect_url", "has_upload_image",
            },
        ),
    ]

    def mautic_manage_subscription_url(self, obj):
        return f"https://moj.djnd.si/{obj.slug}/urejanje-narocnine?token={{contactfield=token}}&email={{contactfield=email}}"

    def mautic_confirm_subscription_url(self, obj):
        if obj.add_to_newsletter_confirmation_required:
            return f"https://moj.djnd.si/{obj.slug}/prijava-uspesna?segment_id={obj.segment}&token={{contactfield=token}}&email={{contactfield=email}}"
        else:
            return "/"


class TransactionAdmin(ImportExportModelAdmin):
    readonly_fields = ("subscriber", "campaign", "transaction_id", "amount", "address")
    list_display = (
        "amount",
        "subscriberName",
        "address",
        "is_paid",
        "created",
        "payment_method",
        "campaign",
    )
    list_filter = ("amount", "campaign", "is_paid", "payment_method")
    resource_class = TransactionResource
    search_fields = ["subscriber__token", "transaction_id"]

    def subscriberName(self, obj):
        if obj.subscriber:
            return obj.subscriber.name
        else:
            return ""

    def address(self, obj):
        if obj.subscriber:
            return obj.subscriber.address
        else:
            return ""


class SubscriptionAdmin(ImportExportModelAdmin):
    readonly_fields = ("subscriber", "campaign", "subscription_id", "amount", "address")
    list_display = (
        "amount",
        "subscriberName",
        "address",
        "created",
        "campaign",
        "subscription_id",
        "is_active",
    )
    list_filter = ("amount", "campaign")
    resource_class = SubscriptionResource
    search_fields = ["subscriber__token", "subscription_id"]

    def subscriberName(self, obj):
        if obj.subscriber:
            return obj.subscriber.name
        else:
            return ""

    def address(self, obj):
        if obj.subscriber:
            return obj.subscriber.address
        else:
            return ""


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(DonationCampaign, DonationCampaignAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
