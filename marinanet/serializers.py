from rest_framework import serializers

from marinanet.models import (
    BunkerData,
    FreshWaterData,
    HeavyWeatherData,
    NoonReportAtSea,
    ReportHeader,
    WeatherData
)


class ReportHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportHeader
        read_only_fields = ['uuid', 'date_created', 'date_modified']


class NoonReportAtSeaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoonReportAtSea
        read_only_fields = ['report_header', 'date_created', 'date_modified']


class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        read_only_fields = ['report_header', 'date_created', 'date_modified']


class HeavyWeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeavyWeatherData
        read_only_fields = ['report_header', 'date_created', 'date_modified']


class BunkerDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BunkerData
        read_only_fields = ['report_header', 'date_created', 'date_modified']


class FreshWaterDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreshWaterData
        read_only_fields = ['report_header', 'date_created', 'date_modified']
