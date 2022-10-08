from django.db import transaction
from rest_framework import serializers

from marinanet.models import (
    BunkerData,
    Company,
    FreshWaterData,
    HeavyWeatherData,
    NoonReportAtSea,
    Profile,
    ReportHeader,
    Ship,
    ShipUser,
    Voyage,
    WeatherData
)
from marinanet.utils import parse_dm


# User Model Serializers

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['uuid', 'name', 'link']
        read_only_fields = ['uuid']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['uuid']


class ShipSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = Ship
        fields = ['uuid', 'name', 'imo_reg', 'company', 'ship_type']
        read_only_fields = ['uuid', 'name', 'imo_reg', 'company']


class ShipUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipUser
        fields = '__all__'
        read_only_fields = ['uuid']


# Report Model Serializers

class VoyageSerializer(serializers.ModelSerializer):
    ship = ShipSerializer(read_only=True)

    class Meta:
        model = Voyage
        fields = ['uuid', 'ship', 'voyage_num',
                  'departure_date', 'departure_port',
                  'arrival_date', 'arrival_port']
        read_only_fields = ['uuid', 'ship']


class ReportHeaderSerializer(serializers.ModelSerializer):
    # latitude = serializers.CharField(max_length=10)
    # longitude = serializers.CharField(max_length=10)

    # def validate_position(self, value):
    #     if not value:
    #         value = parse_dm(latitude, longitude)
    #     return value

    class Meta:
        model = ReportHeader
        fields = '__all__'
        read_only_fields = ['uuid', 'date_created', 'date_modified']


class NoonReportAtSeaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoonReportAtSea
        fields = '__all__'
        read_only_fields = ['report_header', 'date_created', 'date_modified']


class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = '__all__'
        read_only_fields = ['report_data', 'date_created', 'date_modified']


class HeavyWeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeavyWeatherData
        fields = '__all__'
        read_only_fields = ['report_data', 'date_created', 'date_modified']


class BunkerDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BunkerData
        fields = '__all__'
        read_only_fields = ['report_data', 'date_created', 'date_modified']


class FreshWaterDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreshWaterData
        fields = '__all__'
        read_only_fields = ['report_data', 'date_created', 'date_modified']


class NoonReportAtSeaViewSerializer(serializers.ModelSerializer):
    noonreportatsea = NoonReportAtSeaSerializer()
    weatherdata = WeatherDataSerializer()
    heavyweatherdata = HeavyWeatherDataSerializer(required=False)
    bunkerdata_set = BunkerDataSerializer(many=True)
    freshwaterdata = FreshWaterDataSerializer()

    class Meta:
        model = ReportHeader
        fields = '__all__'

    def create(self, validated_data):
        report_data = validated_data.pop('noonreportatsea')
        weather_data = validated_data.pop('weatherdata')
        # heavy_weather = validated_data.pop('heavy_weather_data')
        bunker_data_set = validated_data.pop('bunkerdata_set')
        freshwater_data = validated_data.pop('freshwaterdata')

        with transaction.atomic():
            header = ReportHeader.objects.create(**validated_data)
            NoonReportAtSea.objects.create(report_header=header, **report_data)
            WeatherData.objects.create(report_data=header, **weather_data)
            for bunker_data in bunker_data_set:
                BunkerData.objects.create(report_data=header, **bunker_data)
            FreshWaterData.objects.create(report_data=header, **freshwater_data)

        return header
