import pytz

from django.db import transaction
from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from marinanet.models import (
    Company,
    ConsumptionConditionData,
    DistancePerformanceData,
    FreshWaterData,
    FuelOilData,
    HeavyWeatherData,
    LubricatingOilData,
    ReportHeader,
    Route,
    Ship,
    ShipUser,
    StoppageData,
    UserProfile,
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


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
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
        fields = ['uuid', 'ship', 'voyage_num']
        read_only_fields = ['uuid', 'ship']


class ReportHeaderSerializer(serializers.ModelSerializer):
    report_tz = TimeZoneSerializerField()
    # latitude = serializers.CharField(max_length=10)
    # longitude = serializers.CharField(max_length=10)

    # def validate_position(self, value):
    #     if not value:
    #         value = parse_dm(latitude, longitude)
    #     return value

    class Meta:
        model = ReportHeader
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'modified_at']


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class HeavyWeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeavyWeatherData
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class DistancePerformanceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistancePerformanceData
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class StoppageDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoppageData
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class FuelOilDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelOilData
        exclude = ['ccdata', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class LubricatingOilDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LubricatingOilData
        exclude = ['ccdata', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class FreshWaterDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreshWaterData
        exclude = ['ccdata', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class ConsumptionConditionDataSerializer(serializers.ModelSerializer):
    fueloildata_set = FuelOilDataSerializer(many=True)
    lubricatingoildata_set = LubricatingOilDataSerializer(many=True)
    freshwaterdata_set = FreshWaterDataSerializer(many=True)

    class Meta:
        model = ConsumptionConditionData
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class NoonReportViewSerializer(serializers.ModelSerializer):
    route = RouteSerializer()
    weatherdata = WeatherDataSerializer()
    heavyweatherdata = HeavyWeatherDataSerializer(required=False)
    distanceperformancedata = DistancePerformanceDataSerializer()
    consumptionconditiondata = ConsumptionConditionDataSerializer()
    stoppagedata = StoppageDataSerializer(required=False)

    report_tz = TimeZoneSerializerField()

    class Meta:
        model = ReportHeader
        fields = '__all__'
        exlude = ['report_tz']

    def create(self, validated_data):
        route = validated_data.pop('route')
        weather_data = validated_data.pop('weatherdata')
        heavyweatherdata = validated_data.pop('heavyweatherdata', None)
        distanceperformancedata = validated_data.pop('distanceperformancedata')
        consumptionconditiondata = validated_data.pop('consumptionconditiondata')
        stoppagedata = validated_data.pop('stoppagedata', None)

        with transaction.atomic():
            header = ReportHeader.objects.create(**validated_data)
            Route.objects.create(report_header=header, **route)
            WeatherData.objects.create(report_header=header, **weather_data)
            if heavyweatherdata:
                HeavyWeatherData.objects.create(report_header=header, **heavyweatherdata)
            DistancePerformanceData.objects.create(
                report_header=header, **distanceperformancedata)
            if stoppagedata:
                StoppageData.objects.create(report_header=header, **stoppagedata)

            fueloildata_set = consumptionconditiondata.pop('fueloildata_set')
            lubricatingoildata_set = consumptionconditiondata.pop('lubricatingoildata_set')
            freshwaterdata_set = consumptionconditiondata.pop('freshwaterdata_set')

            ccdata = ConsumptionConditionData.objects.create(report_header=header, **consumptionconditiondata)
            for fueloildata in fueloildata_set:
                FuelOilData.objects.create(ccdata=ccdata, **fueloildata)
            for lubricatingoildata in lubricatingoildata_set:
                LubricatingOilData.objects.create(ccdata=ccdata, **lubricatingoildata)
            for freshwaterdata in freshwaterdata_set:
                FreshWaterData.objects.create(ccdata=ccdata, **freshwaterdata)

        return header
