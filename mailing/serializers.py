from rest_framework import serializers

from mailing import models


class Mailing(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(), many=True
    )
    operators = serializers.PrimaryKeyRelatedField(
        queryset=models.MobileOperator.objects.all(), many=True
    )

    class Meta:
        model = models.Mailing
        fields = '__all__'


class Client(serializers.ModelSerializer):
    class Meta:
        model = models.Client
        fields = '__all__'


class MobileOperator(serializers.ModelSerializer):
    class Meta:
        model = models.MobileOperator
        fields = '__all__'


class Tag(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = '__all__'


class MailingStatistic(serializers.Serializer):
    mailing_id = serializers.IntegerField()
    not_sent = serializers.IntegerField(default=0)
    sent = serializers.IntegerField(default=0)
