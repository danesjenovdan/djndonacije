from rest_framework import serializers

from djnd_supporters import models


class ImageSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(read_only=True)
    donation_amount = serializers.SerializerMethodField()
    class Meta:
        model = models.Image
        fields = ['id', 'image', 'thumbnail', 'url', 'donation_amount']
    def get_donation_amount(self, obj):
        return obj.donation.amount
