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
        fields = '__all__'
        read_only_fields = ['uuid']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['uuid']


class ShipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ship
        fields = ['uuid', 'name', 'company', 'imo_reg', 'ship_type']
        read_only_fields = ['uuid', 'name', 'company', 'imo_reg']


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
        fields = '__all__'
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
        read_only_fields = ['report_header', 'date_created', 'date_modified']


class HeavyWeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeavyWeatherData
        fields = '__all__'
        read_only_fields = ['report_header', 'date_created', 'date_modified']


class BunkerDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BunkerData
        fields = '__all__'
        read_only_fields = ['report_header', 'date_created', 'date_modified']


class FreshWaterDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreshWaterData
        fields = '__all__'
        read_only_fields = ['report_header', 'date_created', 'date_modified']
