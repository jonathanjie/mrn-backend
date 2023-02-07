from rest_framework import serializers

from core.models import (
    Company,
)
from vesselreporting.models.report_models import (
    ActualPerformanceData,
    ArrivalFWETimeAndPosition,
    ArrivalPilotStation,
    ArrivalStandbyTimeAndPosition,
    BDNData,
    CargoOperation,
    ConsumptionConditionData,
    DeparturePilotStation,
    DepartureRunUp,
    DepartureVesselCondition,
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
    PerformanceData,
    PlannedOperations,
    ReportHeader,
    ReportRoute,
    SailingPlan,
    StoppageData,
    TotalConsumptionData,
    UserProfile,
    Voyage,
    VoyageLeg,
    VoyageLegData,
    WeatherData,
)
from vesselreporting.models.ship_models import (
    Ship,
    ShipSpecs,
    ShipUser,
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
        fields = ['uuid', 'voyage', 'leg_num']
        read_only_fields = ['uuid', 'voyage']


class VoyageLegWithVoyageSerializer(serializers.ModelSerializer):
    voyage = VoyageSerializer()
    load_condition = serializers.CharField(
        max_length=16,
        source='voyagelegdata.load_condition')

    class Meta:
        model = VoyageLeg
        fields = ['uuid', 'voyage', 'leg_num', 'load_condition']
        read_only_fields = ['uuid', 'voyage']


class VoyageLegWithPortsSerializer(serializers.ModelSerializer):
    departure_port = serializers.CharField(
        max_length=6, source='voyagelegdata.departure_port')
    departure_date = serializers.DateTimeField(
        source='voyagelegdata.departure_date')
    departure_tz = serializers.FloatField(
        source='voyagelegdata.departure_tz')
    arrival_port = serializers.CharField(
        max_length=6, source='voyagelegdata.arrival_port')
    arrival_date = serializers.DateTimeField(
        source='voyagelegdata.arrival_date')
    arrival_tz = serializers.FloatField(
        source='voyagelegdata.departure_tz')

    class Meta:
        model = VoyageLeg
        exclude = ['uuid', 'created_at', 'modified_at']
        read_only_fields = ['uuid', 'voyage']


class VoyageLegDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoyageLegData
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


class ReportHeaderWithRouteSerializer(serializers.ModelSerializer):
    departure_port = serializers.CharField(
        max_length=6, source='reportroute.departure_port')
    departure_date = serializers.DateTimeField(
        source='reportroute.departure_date')
    departure_tz = serializers.FloatField(
        source='reportroute.departure_tz')
    arrival_port = serializers.CharField(
        max_length=6, source='reportroute.arrival_port')
    arrival_date = serializers.DateTimeField(
        source='reportroute.arrival_date')
    arrival_tz = serializers.FloatField(
        source='reportroute.departure_tz')

    class Meta:
        model = ReportHeader
        fields = '__all__'
        read_only_fields = ['uuid', 'created_at', 'modified_at']


class VoyageLegWithReportsSerializer(serializers.ModelSerializer):
    reports = ReportHeaderWithRouteSerializer(
        many=True, source='reportheader_set')
    load_condition = serializers.CharField(
        max_length=16,
        source='voyagelegdata.load_condition')

    class Meta:
        model = VoyageLeg
        exclude = ['created_at', 'modified_at']
        read_only_fields = ['uuid', 'voyage']


class VoyageWithVoyageLegsSerializer(serializers.ModelSerializer):
    voyage_legs = VoyageLegWithReportsSerializer(
        many=True, source='voyageleg_set')

    class Meta:
        model = Voyage
        exclude = ['created_at', 'modified_at']
        read_only_fields = ['uuid', 'ship']


# class VoyageReportsSerializer(serializers.ModelSerializer):
#     reports = serializers.SerializerMethodField()

#     class Meta:
#         model = Voyage
#         fields = ['uuid', 'ship', 'voyage_num', 'reports']
#         read_only_fields = ['uuid', 'ship']

#     def get_reports(self, obj):
#         voyage_legs = obj.voyageleg_set.all().select_related(
#             'voyagelegdata')
#         report_headers = []
#         for voyage_leg in voyage_legs:
#             report_headers.extend(voyage_leg.reportheader_set.all())
#         serializer = ReportHeaderWithRouteSerializer(report_headers, many=True)
#         return serializer.data


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


class DistanceTimeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistanceTimeData
        exclude = ['report_header', 'created_at', 'modified_at']
        read_only_fields = ['uuid']


class PerformanceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceData
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


class SailingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SailingPlan
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
