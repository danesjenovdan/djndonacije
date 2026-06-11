from django.conf import settings
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


class QuestionSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = models.CampaignQuestion
        fields = [
            "id",
            "url",
            "question_sl",
            "question_en",
            "url_text_sl",
            "url_text_en",
            "field_type",
        ]

    def get_url(self, obj):
        if obj.link:
            return obj.link
        return None


class DonationCampaignSerializer(serializers.ModelSerializer):
    amounts = AmountSerializer(many=True)
    questions = QuestionSerializer(many=True)
    active_monthly_subscriptions = serializers.SerializerMethodField()

    def get_active_monthly_subscriptions(self, obj):
        return obj.subscriptions.filter(is_active=True).count()

    class Meta:
        model = models.DonationCampaign
        fields = [
            "id",
            "has_upn",
            "has_flik",
            "has_flik_subscription",
            "has_braintree",
            "has_braintree_subscription",
            "segment",
            "name",
            "amounts",
            "questions",
            "title",
            "title_en",
            "subtitle",
            "subtitle_en",
            "redirect_url",
            "css_file",
            "active_monthly_subscriptions",
            "terms_of_use",
            "terms_of_use_text_sl",
            "terms_of_use_text_en",
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    campaign = DonationCampaignSerializer()

    class Meta:
        model = models.Subscription
        fields = ["id", "subscription_id", "campaign", "amount", "type", "created"]
