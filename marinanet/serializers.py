from django.db import transaction
from rest_framework import serializers

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
        fields = '__all__'
        read_only_fields = ['report_header', 'created_at', 'modified_at']


class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = '__all__'
        read_only_fields = ['report_header', 'created_at', 'modified_at']


class HeavyWeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeavyWeatherData
        fields = '__all__'
        read_only_fields = ['report_header', 'created_at', 'modified_at']


class DistancePerformanceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistancePerformanceData
        fields = '__all__'
        read_only_fields = ['report_header', 'created_at', 'modified_at']


class StoppageDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoppageData
        fields = '__all__'
        read_only_fields = ['report_header', 'created_at', 'modified_at']


class FuelOilDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelOilData
        fields = '__all__'
        read_only_fields = ['ccdata', 'created_at', 'modified_at']


class LubricatingOilDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LubricatingOilData
        fields = '__all__'
        read_only_fields = ['ccdata', 'created_at', 'modified_at']


class FreshWaterDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreshWaterData
        fields = '__all__'
        read_only_fields = ['ccdata', 'created_at', 'modified_at']


class ConsumptionConditionDataSerializer(serializers.ModelSerializer):
    fueloildata_set = FuelOilDataSerializer(many=True)
    lubricatingoildata_set = LubricatingOilDataSerializer(many=True)
    freshwaterdata = FreshWaterDataSerializer()

    class Meta:
        model = ConsumptionConditionData
        fields = '__all__'
        read_only_fields = ['report_header', 'created_at', 'modified_at']


class NoonReportViewSerializer(serializers.ModelSerializer):
    route = RouteSerializer()
    weatherdata = WeatherDataSerializer()
    heavyweatherdata = HeavyWeatherDataSerializer(required=False)
    distanceperformancedata = DistancePerformanceDataSerializer()
    consumptionconditiondata = ConsumptionConditionDataSerializer()
    stoppagedata = StoppageDataSerializer(required=False)

    class Meta:
        model = ReportHeader
        fields = '__all__'

    def create(self, validated_data):
        route = validated_data.pop('route')
        weather_data = validated_data.pop('weatherdata')
        # heavy_weather = validated_data.pop('heavy_weather_data')
        distanceperformancedata = validated_data.pop('distanceperformancedata')
        consumptionconditiondata = validated_data.pop('consumptionconditiondata')
        # stoppagedata = validated_data.pop('stoppagedata')

        with transaction.atomic():
            header = ReportHeader.objects.create(**validated_data)
            Route.objects.create(report_header=header, **report_data)
            WeatherData.objects.create(report_header=header, **weather_data)
            DistancePerformanceData.objects.create(
                report_header=header, **distanceperformancedata)

            fueloildata_set = consumptionconditiondata.pop('fueloildata_set')
            lubricatingoildata_set = consumptionconditiondata.pop('lubricatingoildata_set')
            freshwaterdata = consumptionconditiondata.pop('freshwaterdata')

            ccdata = ConsumptionConditionData.objects.create(report_header=header, **consumptionconditiondata)
            for fueloildata in fueloildata_set:
                FuelOilData.objects.create(ccdata=ccdata, **fueloildata)
            for lubricatingoildata in lubricatingoildata_set:
                LubricatingOilData.objects.create(ccdata=ccdata, **lubricatingoildata)
            FreshWaterData.objects.create(ccdata=ccdata, **freshwaterdata)

        return header
