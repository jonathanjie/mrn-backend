from django.db import transaction
from rest_framework import serializers

from vesselreporting.models.report_models import ReportHeader
from vesselreporting.serializers.model_serializers import (
    ActualPerformanceDataSerializer,
    ArrivalFWETimeandPositionSerializer,
    ArrivalPilotStationSerializer,
    ArrivalStandbyTimeAndPositionSerializer,
    BDNDataSerializer,
    CargoOperationSerializer,
    ConsumptionConditionDataSerializer,
    DeparturePilotStationSerializer,
    DepartureRunUpSerializer,
    DepartureVesselConditionSerializer,
    DistanceTimeDataSerializer,
    EventDataSerializer,
    HeavyWeatherDataSerializer,
    NoonReportTimeAndPositionSerializer,
    PerformanceDataSerializer,
    PlannedOperationsSerializer,
    ReportRouteSerializer,
    SailingPlanSerializer,
    StoppageDataSerializer,
    TotalConsumptionDataSerializer,
    VoyageSerializer,
    VoyageLegWithVoyageSerializer,
    WeatherDataSerializer,
)
from vesselreporting.logic.report_logic import (
    create_arrival_fwe_report,
    create_arrival_standby_report,
    create_bdn_report,
    create_departure_cosp_report,
    create_departure_standby_report,
    create_event_report,
    create_noon_report,
)


class BaseReportViewSerializer(serializers.ModelSerializer):
    voyage_leg = VoyageLegWithVoyageSerializer(read_only=True)

    class Meta:
        model = ReportHeader
        fields = '__all__'
        exclude = ['id', 'created_at', 'modified_at']


class NoonReportViewSerializer(BaseReportViewSerializer):
    reportroute = ReportRouteSerializer()
    noonreporttimeandposition = NoonReportTimeAndPositionSerializer()
    weatherdata = WeatherDataSerializer()
    heavyweatherdata = HeavyWeatherDataSerializer(
        required=False, allow_null=True)
    distancetimedata = DistanceTimeDataSerializer()
    performancedata = PerformanceDataSerializer()
    consumptionconditiondata = ConsumptionConditionDataSerializer()
    stoppagedata = StoppageDataSerializer(required=False, allow_null=True)

    class Meta:
        model = ReportHeader
        fields = '__all__'

    def create(self, validated_data) -> ReportHeader:
        reportroute = validated_data.pop('reportroute')
        noonreporttimeandposition = validated_data.pop(
            'noonreporttimeandposition')
        weatherdata = validated_data.pop('weatherdata')
        heavyweatherdata = validated_data.pop('heavyweatherdata', None)
        distancetimedata = validated_data.pop('distancetimedata')
        performancedata = validated_data.pop('performancedata')
        consumptionconditiondata = validated_data.pop(
            'consumptionconditiondata')
        stoppagedata = validated_data.pop('stoppagedata', None)

        with transaction.atomic():
            header = create_noon_report(
                reportheader=validated_data,
                reportroute=reportroute,
                noonreporttimeandposition=noonreporttimeandposition,
                weatherdata=weatherdata,
                distancetimedata=distancetimedata,
                performancedata=performancedata,
                consumptionconditiondata=consumptionconditiondata,
                heavyweatherdata=heavyweatherdata,
                stoppagedata=stoppagedata,
            )
        return header


class DepartureStandbyReportViewSerializer(BaseReportViewSerializer):
    reportroute = ReportRouteSerializer()
    cargooperation = CargoOperationSerializer()
    departurevesselcondition = DepartureVesselConditionSerializer()
    departurepilotstation = DeparturePilotStationSerializer(
        required=False, allow_null=True)
    consumptionconditiondata = ConsumptionConditionDataSerializer()
    totalconsumptiondata = TotalConsumptionDataSerializer()

    class Meta:
        model = ReportHeader
        fields = '__all__'

    def create(self, validated_data) -> ReportHeader:
        reportroute = validated_data.pop('reportroute')
        cargooperation = validated_data.pop('cargooperation')
        departurevesselcondition = validated_data.pop(
            'departurevesselcondition')
        departurepilotstation = validated_data.pop(
            'departurepilotstation', None)
        consumptionconditiondata = validated_data.pop(
            'consumptionconditiondata')
        totalconsumptiondata = validated_data.pop('totalconsumptiondata')

        with transaction.atomic():
            header = create_departure_standby_report(
                reportheader=validated_data,
                reportroute=reportroute,
                cargooperation=cargooperation,
                departurevesselcondition=departurevesselcondition,
                consumptionconditiondata=consumptionconditiondata,
                totalconsumptiondata=totalconsumptiondata,
                departurepilotstation=departurepilotstation,
            )
        return header


class DepartureCOSPReportViewSerializer(BaseReportViewSerializer):
    reportroute = ReportRouteSerializer()
    departurepilotstation = DeparturePilotStationSerializer(
        required=False, allow_null=True)
    arrivalpilotstation = ArrivalPilotStationSerializer(
        required=False, allow_null=True)
    departurerunup = DepartureRunUpSerializer()
    distancetimedata = DistanceTimeDataSerializer()
    sailingplan = SailingPlanSerializer()
    consumptionconditiondata = ConsumptionConditionDataSerializer()

    class Meta:
        model = ReportHeader
        fields = '__all__'

    def create(self, validated_data) -> ReportHeader:
        reportroute = validated_data.pop('reportroute')
        departurepilotstation = validated_data.pop(
            'departurepilotstation', None)
        arrivalpilotstation = validated_data.pop(
            'arrivalpilotstation', None)
        departurerunup = validated_data.pop('departurerunup')
        distancetimedata = validated_data.pop('distancetimedata')
        sailingplan = validated_data.pop('sailingplan')
        consumptionconditiondata = validated_data.pop(
            'consumptionconditiondata')

        with transaction.atomic():
            header = create_departure_cosp_report(
                reportheader=validated_data,
                reportroute=reportroute,
                departurerunup=departurerunup,
                distancetimedata=distancetimedata,
                sailingplan=sailingplan,
                consumptionconditiondata=consumptionconditiondata,
                departurepilotstation=departurepilotstation,
                arrivalpilotstation=arrivalpilotstation,
            )
        return header


class ArrivalStandbyReportViewSerializer(BaseReportViewSerializer):
    reportroute = ReportRouteSerializer()
    plannedoperations = PlannedOperationsSerializer()
    arrivalstandbytimeandposition = ArrivalStandbyTimeAndPositionSerializer()
    weatherdata = WeatherDataSerializer()
    distancetimedata = DistanceTimeDataSerializer()
    performancedata = PerformanceDataSerializer()
    arrivalpilotstation = ArrivalPilotStationSerializer(
        required=False, allow_null=True)
    consumptionconditiondata = ConsumptionConditionDataSerializer()
    actualperformancedata = ActualPerformanceDataSerializer()
    totalconsumptiondata = TotalConsumptionDataSerializer()

    class Meta:
        model = ReportHeader
        fields = '__all__'

    def create(self, validated_data) -> ReportHeader:
        reportroute = validated_data.pop('reportroute')
        plannedoperations = validated_data.pop('plannedoperations')
        arrivalstandbytimeandposition = validated_data.pop(
            'arrivalstandbytimeandposition')
        weatherdata = validated_data.pop('weatherdata')
        distancetimedata = validated_data.pop('distancetimedata')
        performancedata = validated_data.pop('performancedata')
        arrivalpilotstation = validated_data.pop('arrivalpilotstation', None)
        consumptionconditiondata = validated_data.pop(
            'consumptionconditiondata')
        actualperformancedata = validated_data.pop('actualperformancedata')
        totalconsumptiondata = validated_data.pop('totalconsumptiondata')

        with transaction.atomic():
            header = create_arrival_standby_report(
                reportheader=validated_data,
                reportroute=reportroute,
                plannedoperations=plannedoperations,
                arrivalstandbytimeandposition=arrivalstandbytimeandposition,
                weatherdata=weatherdata,
                distancetimedata=distancetimedata,
                performancedata=performancedata,
                consumptionconditiondata=consumptionconditiondata,
                actualperformancedata=actualperformancedata,
                totalconsumptiondata=totalconsumptiondata,
                arrivalpilotstation=arrivalpilotstation,
            )
        return header


class ArrivalFWEReportViewSerializer(BaseReportViewSerializer):
    reportroute = ReportRouteSerializer()
    arrivalfwetimeandposition = ArrivalFWETimeandPositionSerializer()
    plannedoperations = PlannedOperationsSerializer()
    arrivalpilotstation = ArrivalPilotStationSerializer(
        required=False, allow_null=True)
    distancetimedata = DistanceTimeDataSerializer()
    consumptionconditiondata = ConsumptionConditionDataSerializer()
    actualperformancedata = ActualPerformanceDataSerializer()
    totalconsumptiondata = TotalConsumptionDataSerializer()

    class Meta:
        model = ReportHeader
        fields = '__all__'

    def create(self, validated_data) -> ReportHeader:
        reportroute = validated_data.pop('reportroute')
        arrivalfwetimeandposition = validated_data.pop(
            'arrivalfwetimeandposition')
        plannedoperations = validated_data.pop('plannedoperations')
        arrivalpilotstation = validated_data.pop('arrivalpilotstation', None)
        distancetimedata = validated_data.pop('distancetimedata')
        consumptionconditiondata = validated_data.pop(
            'consumptionconditiondata')
        actualperformancedata = validated_data.pop('actualperformancedata')
        totalconsumptiondata = validated_data.pop('totalconsumptiondata')

        with transaction.atomic():
            header = create_arrival_fwe_report(
                reportheader=validated_data,
                reportroute=reportroute,
                arrivalfwetimeandposition=arrivalfwetimeandposition,
                plannedoperations=plannedoperations,
                distancetimedata=distancetimedata,
                consumptionconditiondata=consumptionconditiondata,
                actualperformancedata=actualperformancedata,
                totalconsumptiondata=totalconsumptiondata,
                arrivalpilotstation=arrivalpilotstation,
            )
        return header


class EventReportViewSerialiazer(BaseReportViewSerializer):
    eventdata = EventDataSerializer()
    plannedoperations = PlannedOperationsSerializer()
    consumptionconditiondata = ConsumptionConditionDataSerializer()

    class Meta:
        model = ReportHeader
        fields = '__all__'

    def create(self, validated_data) -> ReportHeader:
        eventdata = validated_data.pop('eventdata')
        plannedoperations = validated_data.pop('plannedoperations')
        consumptionconditiondata = validated_data.pop(
            'consumptionconditiondata')

        with transaction.atomic():
            header = create_event_report(
                reportheader=validated_data,
                eventdata=eventdata,
                plannedoperations=plannedoperations,
                consumptionconditiondata=consumptionconditiondata,
            )
        return header


class BDNReportViewSerializer(BaseReportViewSerializer):
    bdndata = BDNDataSerializer()

    class Meta:
        model = ReportHeader
        fields = '__all__'

    def create(self, validated_data) -> ReportHeader:
        bdndata = validated_data.pop('bdndata')

        with transaction.atomic():
            header = create_bdn_report(
                reportheader=validated_data,
                bdndata=bdndata,
            )
        return header
