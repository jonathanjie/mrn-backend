from django.db import transaction
from rest_framework import serializers

from carboncalc.models import (
    CalculatedCII,
    CIIConfig,
    EnergyEfficiencyTechnicalFile,
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


class TargetCIISerializer(serializers.ModelSerializer):
    ship = ShipSerializer(read_only=True)

    class Meta:
        model = TargetCII
        fields = '__all__'


class CIIConfigViewSerlaizer(CIIConfigSerializer):
    current_year_cii_target = TargetCIISerializer()

    def create(self, validated_data):
        current_year_cii_target_data = validated_data.pop(
            'current_year_cii_target')
        ship = validated_data.pop('ship')

        with transaction.atomic():
            current_year_cii_target = TargetCII.objects.create(
                ship=ship,
                **current_year_cii_target_data)
            cii_config = CIIConfig.objects.create(
                ship=ship,
                **validated_data)
            cii_config.current_year_cii_target = current_year_cii_target

        return cii_config


class StandardizedDataReportingFileSerializer(serializers.ModelSerializer):
    ship = ShipSerializer(read_only=True)

    class Meta:
        model = StandardizedDataReportingFile
        fields = ['uuid', 'file_name', 's3_file_path',
                  'ship', 'year', 'acceptance_status', 'error_message']


class EnergyEfficiencyTechnicalFileSerializer(serializers.ModelSerializer):
    ship = ShipSerializer(read_only=True)

    class Meta:
        model = EnergyEfficiencyTechnicalFile
        fields = ['uuid', 'file_name', 's3_file_path',
                  'ship', 'energy_efficiency_index_type']


class ShipNestedCalculatedCIISerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculatedCII
        fields = ['year', 'value', 'grade']


class ShipOverviewCIISerializer(serializers.ModelSerializer):
    size = serializers.DecimalField(
        max_digits=10, decimal_places=2, source='shipspecs.deadweight_tonnage')
    flag = serializers.CharField(max_length=127, source='shipspecs.flag')
    delivery_date = serializers.DateField(source='shipspecs.delivery_date')
    calculated_ciis = ShipNestedCalculatedCIISerializer(
        many=True,
        read_only=True,
        source='calculatedcii_set')

    class Meta:
        model = Ship
        fields = ['name', 'size', 'flag', 'delivery_date', 'calculated_ciis']
