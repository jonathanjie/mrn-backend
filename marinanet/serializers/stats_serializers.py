from rest_framework import serializers

from marinanet.models import (
    FuelOilData,
    ReportHeader,
    VoyageLeg,
)


class FuelOilStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelOilData
        fields = ['fuel_oil_type', 'total_consumption', 'rob']
        read_only_fields = ['uuid']


class DailyStatSerializer(serializers.ModelSerializer):
    speed = serializers.DecimalField(
        source='performancedata.speed_since_last',
        max_digits=4,
        decimal_places=2)
    distance_observed = serializers.DecimalField(
        source='distancetimedata.distance_observed_since_last',
        max_digits=3,
        decimal_places=0)
    distance_to_go = serializers.DecimalField(
        source='distancetimedata.distance_to_go',
        max_digits=5,
        decimal_places=0)
    fuel_stats = FuelOilStatSerializer(
        source='consumptionconditiondata.fueloildata_set', many=True)

    class Meta:
        model = ReportHeader
        fields = ['report_date',
                  'report_type',
                  'speed',
                  'distance_observed',
                  'distance_to_go',
                  'fuel_stats']


class VesselListDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=255, source='voyage.ship.name')
    ship_type = serializers.CharField(
        max_length=4, source='voyage.ship.ship_type')
    flag = serializers.CharField(
        max_length=127, source='voyage.ship.shipspecs.flag')
    imo_reg = serializers.IntegerField(source='voyage.ship.imo_reg')
    deadweight_tonnage = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        source='voyage.ship.shipspecs.deadweight_tonnage')
    load_condition = serializers.CharField(
        max_length=16,
        source='voyagelegdata.load_condition')
    last_report_date = serializers.DateTimeField(
        source='voyagelegdata.last_report_date')

    class Meta:
        model = VoyageLeg
        fields = ['name',
                  'ship_type',
                  'flag',
                  'imo_reg',
                  'deadweight_tonnage',
                  'load_condition',
                  'last_report_date',
                  ]
