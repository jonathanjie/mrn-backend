from rest_framework import serializers

from marinanet.models import (
    ActualPerformanceData,
    ArrivalFWETimeAndPosition,
    ArrivalPilotStation,
    ArrivalStandbyTimeAndPosition,
    BDNData,
    CargoOperation,
    Company,
    ConsumptionConditionData,
    DeparturePilotStation,
    DepartureRunUp,
    DepartureVesselCondition,
    DistancePerformanceData,
    DistanceTimeData,
    EventData,
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
    PlannedOperations,
    ReportHeader,
    ReportRoute,
    Ship,
    ShipSpecs,
    ShipUser,
    StoppageData,
    TotalConsumptionData,
    TransoceanicBudget,
    UserProfile,
    Voyage,
    VoyageLeg,
    VoyageLegData,
    WeatherData,
)


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


class VoyageLegDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoyageLegData
        fields = '__all__'
        exclude = ['uuid', 'created_at', 'modified_at']


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


class ReportHeaderWithLegSerializer(serializers.ModelSerializer):
    voyage_leg = VoyageLegSerializer()

    class Meta:
        model = ReportHeader
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'modified_at']


# class VoyageReportsSerializer(serializers.ModelSerializer):
#     reports = ReportHeaderSerializer(source='reportheader_set', many=True)

#     class Meta:
#         model = Voyage
#         fields = ['uuid', 'ship', 'voyage_num', 'reports']
#         read_only_fields = ['uuid', 'ship']

class VoyageReportsSerializer(serializers.ModelSerializer):
    reports = serializers.SerializerMethodField()

    class Meta:
        model = Voyage
        fields = ['uuid', 'ship', 'voyage_num', 'reports']
        read_only_fields = ['uuid', 'ship']

    def get_reports(self, obj):
        voyage_legs = obj.voyageleg_set.all()
        report_headers = []
        for voyage_leg in voyage_legs:
            report_headers.extend(voyage_leg.reportheader_set.all())
        serializer = ReportHeaderSerializer(report_headers, many=True)
        return serializer.data


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
        exclude = ['ccdata', 'created_at', 'modified_at', 'id']
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
        exclude = ['ccdata', 'created_at', 'modified_at', 'id']
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


class ArrivalPilotStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArrivalPilotStation
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class DepartureRunUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartureRunUp
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class DistanceTimeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistanceTimeData
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class TransoceanicBudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransoceanicBudget
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class ArrivalStandbyTimeAndPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArrivalStandbyTimeAndPosition
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class PlannedOperationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlannedOperations
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class ArrivalFWETimeandPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArrivalFWETimeAndPosition
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class ActualPerformanceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActualPerformanceData
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
        exclude = ['tcdata', 'created_at', 'modified_at', 'id']
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
        exclude = ['tcdata', 'created_at', 'modified_at', 'id']
        read_only_fields = ['uuid']


class FreshWaterTotalConsumptionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreshWaterTotalConsumptionData
        exclude = ['tcdata', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class TotalConsumptionDataSerializer(serializers.ModelSerializer):
    fueloiltotalconsumptiondata_set = FuelOilTotalConsumptionDataSerializer(
        many=True)
    lubricatingoiltotalconsumptiondata_set = LubricatingOilTotalConsumptionDataSerializer(
        many=True, required=False, allow_null=True)
    freshwatertotalconsumptiondata = FreshWaterTotalConsumptionDataSerializer(
        required=False, allow_null=True)

    class Meta:
        model = TotalConsumptionData
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class EventDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventData
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class BDNDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BDNData
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']
