from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer

from djnd_supporters import models

# Serializers define the API representation.
class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Milestone
        fields = ('name', 'budget')


class ProjectSerializer(serializers.ModelSerializer):
    milestones = MilestoneSerializer(many=True, read_only=True)
    class Meta:
        model = models.Project
        read_only_fields = ('id',)
        fields = ('id', 'name', 'description', 'collected_funds', 'milestones')


class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Donation
        read_only_fields = ('id',)
        fields = ('id', 'project', 'amount', 'subscriber')
        extra_kwargs = {
            'subscriber': {'write_only': True, 'required': False}
        }


class SupporterSerializer(WritableNestedModelSerializer):
    donations = DonationSerializer(many=True)
    donation_amount = serializers.SerializerMethodField()

    class Meta:
        model = models.Supporter
        read_only_fields = ('id',)
        fields = ('id', 'name', 'surename', 'email', 'newsletter', 'is_supporter', 'donations', 'donation_amount')

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        if models.Supporter.objects.filter(email=data.get('email')):
            raise serializers.ValidationError({'email': ['Supporter with this email already exists.']})
        return data

    def get_donation_amount(self, obj):
        return obj.donation_amount


class GiftSerializer(serializers.ModelSerializer):
    donations = DonationSerializer(many=True)
    donation_amount = serializers.SerializerMethodField()

    class Meta:
        model = models.Gift
        read_only_fields = ('id',)
        fields = ('id', 'name', 'email', 'send_at', 'mail_content', 'donations', 'sender')

    def create(self, validated_data):
        donations = validated_data.pop('donations')
        subscriber = models.Gift.objects.create(**validated_data)
        subscriber.username = subscriber.id
        subscriber.save()
        for donation in donations:
            models.Donation.objects.create(subscriber=subscriber, **donation)
        return subscriber

    def donation_amount(self, obj):
        return obj.get_donation_amount()
