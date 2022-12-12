import pytz

from django.db import transaction
from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from marinanet.models import (
    Company,
    ConsumptionConditionData,
    ConsumptionDataCorrection,
    DistancePerformanceData,
    FreshWaterData,
    FuelOilData,
    FuelOilDataCorrection,
    HeavyWeatherData,
    LubricatingOilData,
    LubricatingOilDataCorrection,
    ReportHeader,
    Route,
    Ship,
    ShipSpecs,
    ShipUser,
    StoppageData,
    UserProfile,
    Voyage,
    WeatherData
)
# from marinanet.utils import parse_dm


# User Model Serializers

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['uuid', 'name', 'link']
        read_only_fields = ['uuid']


class UserProfileSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    class Meta:
        model = UserProfile
        fields = ('uuid', 'company', 'role')

class ShipSpecsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipSpecs
        fields = ('flag', 'deadweight_tonnage', 'cargo_unit', 'fuel_options', 'lubricating_oil_options', 'machinery_options', 'propeller_pitch')

class ShipSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    ship_specs = ShipSpecsSerializer()

    class Meta:
        model = Ship
        fields = ['uuid', 'name', 'imo_reg', 'company', 'ship_type', 'ship_specs']
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
        fields = ['uuid', 'ship', 'voyage_num', 'allowed_report_types']
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


class VoyageReportsSerializer(serializers.ModelSerializer):
    reports = ReportHeaderSerializer(source='reportheader_set', many=True)

    class Meta:
        model = Voyage
        fields = ['uuid', 'ship', 'voyage_num', 'reports']
        read_only_fields = ['uuid', 'ship']


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


class FuelOilDataCorrectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelOilDataCorrection
        exclude = ['fuel_oil_data', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class FuelOilDataSerializer(serializers.ModelSerializer):
    fueloildatacorrection = FuelOilDataCorrectionSerializer(required=False)

    class Meta:
        model = FuelOilData
        exclude = ['ccdata', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class LubricatingOilDataCorrectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LubricatingOilDataCorrection
        exclude = ['lubricating_oil_data', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class LubricatingOilDataSerializer(serializers.ModelSerializer):
    lubricatingoildatacorrection = LubricatingOilDataCorrectionSerializer(
        required=False)

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
    freshwaterdata = FreshWaterDataSerializer()

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
        consumptionconditiondata = validated_data.pop(
            'consumptionconditiondata')
        stoppagedata = validated_data.pop('stoppagedata', None)

        with transaction.atomic():
            header = ReportHeader.objects.create(**validated_data)
            Route.objects.create(report_header=header, **route)
            WeatherData.objects.create(report_header=header, **weather_data)
            if heavyweatherdata:
                HeavyWeatherData.objects.create(
                    report_header=header, **heavyweatherdata)
            DistancePerformanceData.objects.create(
                report_header=header, **distanceperformancedata)
            if stoppagedata:
                StoppageData.objects.create(
                    report_header=header, **stoppagedata)

            fueloildata_set = consumptionconditiondata.pop('fueloildata_set')
            lubricatingoildata_set = consumptionconditiondata.pop(
                'lubricatingoildata_set')
            freshwaterdata = consumptionconditiondata.pop(
                'freshwaterdata')

            ccdata = ConsumptionConditionData.objects.create(
                report_header=header, **consumptionconditiondata)
            for fueloildata in fueloildata_set:
                fueloildatacorrection = fueloildata.pop(
                    'fueloildatacorrection', None)
                fo_data = FuelOilData.objects.create(
                    ccdata=ccdata, **fueloildata)
                if fueloildatacorrection:
                    FuelOilDataCorrection.objects.create(
                        fuel_oil_data=fo_data, **fueloildatacorrection)
            for lubricatingoildata in lubricatingoildata_set:
                lubricatingoildatacorrection = lubricatingoildata.pop(
                    'lubricatingoildatacorrection', None)
                lo_data = LubricatingOilData.objects.create(
                    ccdata=ccdata, **lubricatingoildata)
                if lubricatingoildatacorrection:
                    LubricatingOilDataCorrection.objects.create(
                        lubricating_oil_data=lo_data,
                        **lubricatingoildatacorrection)
            FreshWaterData.objects.create(ccdata=ccdata, **freshwaterdata)

        return header
