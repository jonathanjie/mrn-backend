import pytz

from django.db import transaction
from rest_framework import serializers
# from timezone_field.rest_framework import TimeZoneSerializerField

from marinanet.models import (
    CargoOperation,
    Company,
    ConsumptionConditionData,
    DeparturePilotStation,
    DepartureVesselCondition,
    DistancePerformanceData,
    FreshWaterData,
    FreshWaterTotalConsumptionData,
    FuelOilData,
    FuelOilDataCorrection,
    FuelOilTotalConsumptionData,
    FuelOilTotalConsumptionDataCorrection,
    HeavyWeatherData,
    LubricatingOilData,
    LubricatingOilDataCorrection,
    LubricatingOilTotalConsumptionData,
    LubricatingOilTotalConsumptionDataCorrection,
    NoonReportTimeAndPosition,
    ReportHeader,
    ReportRoute,
    Ship,
    ShipSpecs,
    ShipUser,
    StoppageData,
    TotalConsumptionData,
    UserProfile,
    Voyage,
    VoyageLeg,
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
        fields = ('flag', 'deadweight_tonnage', 'cargo_unit', 'fuel_options',
                  'lubricating_oil_options', 'machinery_options',
                  'propeller_pitch')


class ShipSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    shipspecs = ShipSpecsSerializer()

    class Meta:
        model = Ship
        fields = ['uuid', 'name', 'imo_reg',
                  'company', 'ship_type', 'shipspecs']
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


class VoyageLegSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoyageLeg
        fields = ['uuid', 'voyage', 'leg_num',
                  'departure_port', 'departure_date', 'departure_tz',
                  'arrival_port', 'arrival_date', 'arrival_tz']
        read_only_fields = ['uuid', 'voyage']


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


class VoyageReportsSerializer(serializers.ModelSerializer):
    reports = ReportHeaderSerializer(source='reportheader_set', many=True)

    class Meta:
        model = Voyage
        fields = ['uuid', 'ship', 'voyage_num', 'reports']
        read_only_fields = ['uuid', 'ship']


class NoonReportTimeAndPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoonReportTimeAndPosition
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class ReportRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportRoute
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


# class DistinctReportRoutesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ReportRoute
#         fields = ['departure_port', 'arrival_port',
#                   'departure_date', 'arrival_date']


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
    fueloildatacorrection = FuelOilDataCorrectionSerializer(
        required=False, allow_null=True)

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
        required=False, allow_null=True)

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


class CargoOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CargoOperation
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class DepartureVesselConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartureVesselCondition
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class DeparturePilotStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeparturePilotStation
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class FuelOilTotalConsumptionDataCorrectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelOilTotalConsumptionDataCorrection
        exclude = ['fuel_oil_tcdata', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class FuelOilTotalConsumptionDataSerializer(serializers.ModelSerializer):
    fueloiltotalconsumptiondatacorrection = FuelOilTotalConsumptionDataCorrectionSerializer(
        required=False, allow_null=True)

    class Meta:
        model = FuelOilTotalConsumptionData
        exclude = ['tc_data', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class LubricatingOilTotalConsumptionDataCorrectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LubricatingOilTotalConsumptionDataCorrection
        exclude = ['lubricating_oil_tcdata', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class LubricatingOilTotalConsumptionDataSerializer(serializers.ModelSerializer):
    lubricatingoiltotalconsumptiondatacorrection = LubricatingOilTotalConsumptionDataCorrectionSerializer(
        required=False, allow_null=True)

    class Meta:
        model = LubricatingOilTotalConsumptionData
        exclude = ['tc_data', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class FreshWaterTotalConsumptionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreshWaterTotalConsumptionData
        exclude = ['ccdata', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class TotalConsumptionDataSerializer(serializers.ModelSerializer):
    fueloiltotalconsumptiondata_set = FuelOilTotalConsumptionDataSerializer(many=True)
    lubricatingoiltotalconsumptiondata_set = LubricatingOilTotalConsumptionDataSerializer(many=True)
    freshwatertotalconsumptiondata = FreshWaterTotalConsumptionDataSerializer()

    class Meta:
        model = TotalConsumptionData
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class NoonReportViewSerializer(serializers.ModelSerializer):
    reportroute = ReportRouteSerializer()
    noonreporttimeandposition = NoonReportTimeAndPositionSerializer()
    weatherdata = WeatherDataSerializer()
    heavyweatherdata = HeavyWeatherDataSerializer(
        required=False, allow_null=True)
    distanceperformancedata = DistancePerformanceDataSerializer()
    consumptionconditiondata = ConsumptionConditionDataSerializer()
    stoppagedata = StoppageDataSerializer(required=False, allow_null=True)

    class Meta:
        model = ReportHeader
        fields = '__all__'

    def create(self, validated_data):
        reportroute = validated_data.pop('reportroute')
        noonreporttimeandposition = validated_data.pop('noonreporttimeandposition')
        weatherdata = validated_data.pop('weatherdata')
        heavyweatherdata = validated_data.pop('heavyweatherdata', None)
        distanceperformancedata = validated_data.pop('distanceperformancedata')
        consumptionconditiondata = validated_data.pop(
            'consumptionconditiondata')
        stoppagedata = validated_data.pop('stoppagedata', None)

        with transaction.atomic():
            header = ReportHeader.objects.create(**validated_data)
            ReportRoute.objects.create(report_header=header, **reportroute)
            NoonReportTimeAndPosition.objects.create(report_header=header, **noonreporttimeandposition)
            WeatherData.objects.create(report_header=header, **weatherdata)
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


class DepartureStandbyReportViewSerializer(serializers.ModelSerializer):
    reportroute = ReportRouteSerializer()
    cargooperation = CargoOperationSerializer()
    departurevesselcondition = DepartureVesselConditionSerializer()
    departurepilotstation = DeparturePilotStationSerializer(required=False, allow_null=True)
    consumptionconditiondata = ConsumptionConditionDataSerializer()
    totalconsumptiondata = TotalConsumptionDataSerializer()

    class Meta:
        model = ReportHeader
        fields = '__all__'

    def create(self, validated_data):
        reportroute = validated_data.pop('reportroute')
        cargooperation = validated_data.pop('cargooperation')
        departurevesselcondition = validated_data.pop('departurevesselcondition')
        departurepilotstation = validated_data.pop('departurepilotstation', None)
        consumptionconditiondata = validated_data.pop('consumptionconditiondata')
        totalconsumptiondata = validated_data.pop('totalconsumptiondata')

        with transaction.atomic():
            header = ReportHeader.objects.create(**validated_data)
            ReportRoute.objects.create(report_header=header, **reportroute)
            CargoOperation.objects.create(report_header=header, **cargooperation)
            DepartureVesselCondition.objects.create(report_header=header, **departurevesselcondition)
            if departurepilotstation:
                DeparturePilotStation.objects.create(report_header=header, **departurepilotstation)

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

            fueloiltotalconsumptiondata_set = totalconsumptiondata.pop('fueloiltotalconsumptiondata_set')
            lubricatingoiltotalconsumptiondata_set = totalconsumptiondata.pop(
                'lubricatingoiltotalconsumptiondata_set')
            freshwatertotalconsumptiondata = totalconsumptiondata.pop(
                'freshwatertotalconsumptiondata')

            tcdata = TotalConsumptionData.objects.create(
                report_header=header, **totalconsumptiondata)
            for fueloiltotalconsumptiondata in fueloiltotalconsumptiondata_set:
                fueloiltotalconsumptiondatacorrection = fueloiltotalconsumptiondata.pop(
                    'fueloiltotalconsumptiondatacorrection', None)
                fo_tcdata = FuelOilTotalConsumptionData.objects.create(
                    tc_data=tcdata, **fueloiltotalconsumptiondata)
                if fueloiltotalconsumptiondatacorrection:
                    FuelOilTotalConsumptionDataCorrection.objects.create(
                        fuel_oil_tcdata=fo_tcdata, **fueloiltotalconsumptiondatacorrection)
            for lubricatingoiltotalconsumptiondata in lubricatingoiltotalconsumptiondata_set:
                lubricatingoiltotalconsumptiondatacorrection = lubricatingoiltotalconsumptiondata.pop(
                    'lubricatingoiltotalconsumptiondatacorrection', None)
                lo_tcdata = LubricatingOilTotalConsumptionData.objects.create(
                    tc_data=tcdata, **lubricatingoiltotalconsumptiondata)
                if lubricatingoiltotalconsumptiondatacorrection:
                    LubricatingOilTotalConsumptionDataCorrection.objects.create(
                        lubricating_oil_tcdata=lo_tcdata,
                        **lubricatingoiltotalconsumptiondatacorrection)
            FreshWaterTotalConsumptionData.objects.create(ccdata=tcdata, **freshwatertotalconsumptiondata)

        return header


class ArrivalStandByReportViewSerializer(serializers.ModelSerializer):
    route = ReportRouteSerializer()
    weatherdata = WeatherDataSerializer()
    heavyweatherdata = HeavyWeatherDataSerializer(required=False)
    distanceperformancedata = DistancePerformanceDataSerializer()
    consumptionconditiondata = ConsumptionConditionDataSerializer()
    stoppagedata = StoppageDataSerializer(required=False)

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
            ReportRoute.objects.create(report_header=header, **route)
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
