from rest_framework import serializers

from vesselreporting.models.report_models import (
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


class ShipOverviewSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    ship_type = serializers.CharField(max_length=4)

    # Default to None if Ship Specs have not been initialized
    flag = serializers.CharField(
        max_length=127,
        source='shipspecs.flag',
        default=None)
    imo_reg = serializers.IntegerField()
    deadweight_tonnage = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        source='shipspecs.deadweight_tonnage')

    # Default to None if no voyage or legs have been created
    load_condition = serializers.CharField(
        max_length=16,
        source='latest_leg.voyagelegdata.load_condition',
        default=None)
    last_report_type = serializers.CharField(
        max_length=4,
        source='latest_leg.voyagelegdata.last_report_type',
        default=None)
    last_report_date = serializers.DateTimeField(
        source='latest_leg.voyagelegdata.last_report_date',
        default=None)
    last_report_tz = serializers.FloatField(
        source='latest_leg.voyagelegdata.last_report_tz',
        default=None)
    last_operation = serializers.JSONField(
        source='latest_leg.voyagelegdata.last_operation',
        default=None)

    class Meta:
        model = VoyageLeg
        fields = ['name', 'ship_type', 'flag', 'imo_reg', 'deadweight_tonnage',
                  'load_condition', 'last_report_type', 'last_report_date',
                  'last_report_tz', 'last_operation']
