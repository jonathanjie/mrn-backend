from rest_framework import serializers

from marinanet.models import (
    FuelOilData,
    ReportHeader,
)


class FuelOilStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelOilData
        fields = ['fuel_oil_type', 'total_consumption', 'rob']
        read_only_fields = ['uuid']


class DailyStatSerializer(serializers.ModelSerializer):
    speed = serializers.DecimalField(
        source='distanceperformancedata.speed_since_noon',
        max_digits=4,
        decimal_places=2)
    distance_observed = serializers.DecimalField(
        source='distanceperformancedata.distance_observed_since_noon',
        max_digits=3,
        decimal_places=0)
    distance_to_go = serializers.DecimalField(
        source='distanceperformancedata.distance_to_go',
        max_digits=5,
        decimal_places=0)
    fuel_stats = FuelOilStatSerializer(
        source='consumptionconditiondata.fueloildata_set', many=True)

    class Meta:
        model = ReportHeader
        fields = ['report_date',
                  'speed',
                  'distance_observed',
                  'distance_to_go',
                  'fuel_stats']
