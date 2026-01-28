from rest_framework import serializers

from djnd_supporters import models


class ImageSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(read_only=True)
    donation_amount = serializers.SerializerMethodField()

    class Meta:
        model = models.Image
        fields = ["id", "image", "thumbnail", "url", "donation_amount"]

    def get_donation_amount(self, obj):
        return obj.donation.amount


class AmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PredefinedAmount
        exclude = ["created", "modified", "id", "donation_campaign"]


class DonationCampaignSerializer(serializers.ModelSerializer):
    amounts = AmountSerializer(many=True)

    class Meta:
        model = models.DonationCampaign
        fields = [
            "id",
            "has_upn",
            "has_flik",
            "has_braintree",
            "has_braintree_subscription",
            "segment",
            "name",
            "amounts",
            "title",
            "title_en",
            "subtitle",
            "subtitle_en",
            "redirect_url",
            "css_file",
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    campaign = DonationCampaignSerializer()

    class Meta:
        model = models.Subscription
        fields = ["id", "subscription_id", "campaign", "amount", "created"]
