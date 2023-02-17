from django.db import transaction
from rest_framework import serializers

from carboncalc.models import (
    CIIConfig,
    TargetCII,
    StandardizedDataReportingFile,
)
from core.models import Ship
from core.serializers import ShipSerializer


class CIIConfigSerializer(serializers.ModelSerializer):
    ship = ShipSerializer(read_only=True)

    class Meta:
        model = CIIConfig
        fields = '__all__'
        exclude = ['id', 'created_at', 'modified_at']


class TargetCIISerializer(serializers.ModelSerializer):
    ship = ShipSerializer(read_only=True)

    class Meta:
        model = TargetCII
        fields = '__all__'
        exclude = ['id', 'created_at', 'modified_at']


class CIIConfigViewSerlaizer(CIIConfigSerializer):
    current_year_cii_target = TargetCIISerializer()

    def create(self, validated_data):
        current_year_cii_target_data = validated_data.pop('targetcii')
        ship = validated_data.pop('ship')

        with transaction.atomic():
            current_year_cii_target = TargetCII.objects.create(
                ship=ship,
                **current_year_cii_target_data)
            cii_config = CIIConfig.objects.create(
                ship=ship,
                **validated_data)

        return cii_config


class StandardizedDataRerportingFileSerializer(serializers.ModelSerializer):
    ship = ShipSerializer(read_only=True)

    class Meta:
        model = StandardizedDataReportingFile
        fields = '__all__'
        exclude = ['id', 'created_at', 'modified_at']
