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

class SubscriberSerializer(WritableNestedModelSerializer):
    donations = DonationSerializer(many=True)
    #donation_amount = serializers.SerializerMethodField()
    donation_amount = serializers.IntegerField()

    def validate(self, data):
        donations = data['donations']
        donation_amount = data.pop('donation_amount')
        if self.instance and donations:
            new_sum = sum([donation['amount'] for donation in donations])
            if self.instance.donation_amount != new_sum:
                if new_sum == donation_amount:
                    return data
                raise serializers.ValidationError(['Donation amount mismatch subscription amount'])
        return data

    def get_donation_amount(self, obj):
        return obj.donation_amount


class SupporterSerializer(SubscriberSerializer):
    class Meta:
        model = models.Supporter
        read_only_fields = ('id',)
        fields = ('id', 'name', 'surname', 'email', 'newsletter', 'is_supporter', 'donations', 'donation_amount')

    def validate_email(self, value):
        """
        Check if upporter with this email exists.
        """
        if models.Supporter.objects.filter(email=value):
            raise serializers.ValidationError(['Supporter with this email already exists.'])
        return data


class GiftSerializer(SubscriberSerializer):
    class Meta:
        model = models.Gift
        read_only_fields = ('id',)
        fields = ('id', 'name', 'email', 'send_at', 'mail_content', 'donations', 'sender')
