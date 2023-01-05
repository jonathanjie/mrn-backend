from django.db import transaction
from rest_framework import serializers

from marinanet.models import (
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
    StoppageData,
    TotalConsumptionData,
    TransoceanicBudget,
    VoyageLeg,
    WeatherData,
)

from marinanet.serializers.model_serializers import (
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
    DistancePerformanceDataSerializer,
    DistanceTimeDataSerializer,
    EventDataSerializer,
    HeavyWeatherDataSerializer,
    NoonReportTimeAndPositionSerializer,
    PlannedOperationsSerializer,
    ReportRouteSerializer,
    StoppageDataSerializer,
    TotalConsumptionDataSerializer,
    TransoceanicBudgetSerializer,
    VoyageSerializer,
    VoyageLegSerializer,
    WeatherDataSerializer,
)


class BaseReportViewSerializer(serializers.ModelSerializer):
    voyage_leg = VoyageLegSerializer()

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
    distanceperformancedata = DistancePerformanceDataSerializer()
    consumptionconditiondata = ConsumptionConditionDataSerializer()
    stoppagedata = StoppageDataSerializer(required=False, allow_null=True)

    class Meta:
        model = ReportHeader
        fields = '__all__'

    def create(self, validated_data):
        reportroute = validated_data.pop('reportroute')
        noonreporttimeandposition = validated_data.pop(
            'noonreporttimeandposition')
        weatherdata = validated_data.pop('weatherdata')
        heavyweatherdata = validated_data.pop('heavyweatherdata', None)
        distanceperformancedata = validated_data.pop('distanceperformancedata')
        consumptionconditiondata = validated_data.pop(
            'consumptionconditiondata')
        stoppagedata = validated_data.pop('stoppagedata', None)

        with transaction.atomic():
            header = ReportHeader.objects.create(**validated_data)
            ReportRoute.objects.create(report_header=header, **reportroute)
            NoonReportTimeAndPosition.objects.create(
                report_header=header, **noonreporttimeandposition)
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

    def create(self, validated_data):
        voyage_leg_data = validated_data.pop('voyage_leg')
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
            voyage_leg = VoyageLeg.objects.create(**voyage_leg_data)
            header = ReportHeader.objects.create(
                voyage_leg=voyage_leg, **validated_data)
            ReportRoute.objects.create(report_header=header, **reportroute)
            CargoOperation.objects.create(
                report_header=header, **cargooperation)
            DepartureVesselCondition.objects.create(
                report_header=header, **departurevesselcondition)
            if departurepilotstation:
                DeparturePilotStation.objects.create(
                    report_header=header, **departurepilotstation)

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

            fueloiltotalconsumptiondata_set = totalconsumptiondata.pop(
                'fueloiltotalconsumptiondata_set')
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
                    tcdata=tcdata, **fueloiltotalconsumptiondata)
                if fueloiltotalconsumptiondatacorrection:
                    FuelOilTotalConsumptionDataCorrection.objects.create(
                        fuel_oil_tcdata=fo_tcdata, **fueloiltotalconsumptiondatacorrection)
            for lubricatingoiltotalconsumptiondata in lubricatingoiltotalconsumptiondata_set:
                lubricatingoiltotalconsumptiondatacorrection = lubricatingoiltotalconsumptiondata.pop(
                    'lubricatingoiltotalconsumptiondatacorrection', None)
                lo_tcdata = LubricatingOilTotalConsumptionData.objects.create(
                    tcdata=tcdata, **lubricatingoiltotalconsumptiondata)
                if lubricatingoiltotalconsumptiondatacorrection:
                    LubricatingOilTotalConsumptionDataCorrection.objects.create(
                        lubricating_oil_tcdata=lo_tcdata,
                        **lubricatingoiltotalconsumptiondatacorrection)
            FreshWaterTotalConsumptionData.objects.create(
                tcdata=tcdata, **freshwatertotalconsumptiondata)

        return header


class DepartureCOSPReportViewSerializer(BaseReportViewSerializer):
    reportroute = ReportRouteSerializer()
    departurepilotstation = DeparturePilotStationSerializer(
        required=False, allow_null=True)
    arrivalpilotstation = ArrivalPilotStationSerializer()
    departurerunup = DepartureRunUpSerializer()
    distancetimedata = DistanceTimeDataSerializer()
    transoceanicbudget = TransoceanicBudgetSerializer()
    consumptionconditiondata = ConsumptionConditionDataSerializer()

    class Meta:
        model = ReportHeader
        fields = '__all__'

    def create(self, validated_data):
        reportroute = validated_data.pop('reportroute')
        departurepilotstation = validated_data.pop(
            'departurepilotstation', None)
        arrivalpilotstation = validated_data.pop('arrivalpilotstation')
        departurerunup = validated_data.pop('departurerunup')
        distancetimedata = validated_data.pop('distancetimedata')
        transoceanicbudget = validated_data.pop('transoceanicbudget')
        consumptionconditiondata = validated_data.pop(
            'consumptionconditiondata')

        with transaction.atomic():
            header = ReportHeader.objects.create(**validated_data)
            ReportRoute.objects.create(report_header=header, **reportroute)
            if departurepilotstation:
                DeparturePilotStation.objects.create(
                    report_header=header, **departurepilotstation)
            ArrivalPilotStation.objects.create(
                report_header=header, **arrivalpilotstation)
            DepartureRunUp.objects.create(
                report_header=header, **departurerunup)
            DistanceTimeData.objects.create(
                report_header=header, **distancetimedata)
            TransoceanicBudget.objects.create(
                report_header=header, **transoceanicbudget)

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


class ArrivalStandbyReportViewSerializer(BaseReportViewSerializer):
    reportroute = ReportRouteSerializer()
    plannedoperations = PlannedOperationsSerializer()
    arrivalstandbytimeandposition = ArrivalStandbyTimeAndPositionSerializer()
    weatherdata = WeatherDataSerializer()
    distanceperformancedata = DistancePerformanceDataSerializer()
    arrivalpilotstation = ArrivalPilotStationSerializer(
        required=False, allow_null=True)
    consumptionconditiondata = ConsumptionConditionDataSerializer()
    actualperformancedata = ActualPerformanceDataSerializer()
    totalconsumptiondata = TotalConsumptionDataSerializer()

    class Meta:
        model = ReportHeader
        fields = '__all__'

    def create(self, validated_data):
        reportroute = validated_data.pop('reportroute')
        plannedoperations = validated_data.pop('plannedoperations')
        arrivalstandbytimeandposition = validated_data.pop(
            'arrivalstandbytimeandposition')
        weatherdata = validated_data.pop('weatherdata')
        distanceperformancedata = validated_data.pop('distanceperformancedata')
        arrivalpilotstation = validated_data.pop('arrivalpilotstation', None)
        consumptionconditiondata = validated_data.pop(
            'consumptionconditiondata')
        actualperformancedata = validated_data.pop('actualperformancedata')
        totalconsumptiondata = validated_data.pop('totalconsumptiondata')

        with transaction.atomic():
            header = ReportHeader.objects.create(**validated_data)
            ReportRoute.objects.create(report_header=header, **reportroute)
            PlannedOperations.objects.create(
                report_header=header, **plannedoperations)
            ArrivalStandbyTimeAndPosition.objects.create(
                report_header=header, **arrivalstandbytimeandposition)
            WeatherData.objects.create(report_header=header, **weatherdata)
            DistancePerformanceData.objects.create(
                report_header=header, **distanceperformancedata)
            if arrivalpilotstation:
                ArrivalPilotStation.objects.create(
                    report_header=header, **arrivalpilotstation)

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

            ActualPerformanceData.objects.create(
                report_header=header, **actualperformancedata)

            fueloiltotalconsumptiondata_set = totalconsumptiondata.pop(
                'fueloiltotalconsumptiondata_set')

            tcdata = TotalConsumptionData.objects.create(
                report_header=header, **totalconsumptiondata)
            for fueloiltotalconsumptiondata in fueloiltotalconsumptiondata_set:
                fo_tcdata = FuelOilTotalConsumptionData.objects.create(
                    tcdata=tcdata, **fueloiltotalconsumptiondata)

        return header


class ArrivalFWEReportViewSerializer(BaseReportViewSerializer):
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

    def create(self, validated_data):
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
            header = ReportHeader.objects.create(**validated_data)
            ArrivalFWETimeAndPosition.objects.create(
                report_header=header, **arrivalfwetimeandposition)
            PlannedOperations.objects.create(
                report_header=header, **plannedoperations)
            if arrivalpilotstation:
                ArrivalPilotStation.objects.create(
                    report_header=header, **arrivalpilotstation)
            DistanceTimeData.objects.create(
                report_header=header, **distancetimedata)

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

            ActualPerformanceData.objects.create(
                report_header=header, **actualperformancedata)

            fueloiltotalconsumptiondata_set = totalconsumptiondata.pop(
                'fueloiltotalconsumptiondata_set')

            tcdata = TotalConsumptionData.objects.create(
                report_header=header, **totalconsumptiondata)
            for fueloiltotalconsumptiondata in fueloiltotalconsumptiondata_set:
                fo_tcdata = FuelOilTotalConsumptionData.objects.create(
                    tcdata=tcdata, **fueloiltotalconsumptiondata)

        return header


class EventReportViewSerialiazer(BaseReportViewSerializer):
    eventdata = EventDataSerializer()
    plannedoperations = PlannedOperationsSerializer()
    consumptionconditiondata = ConsumptionConditionDataSerializer()

    class Meta:
        model = ReportHeader
        fields = '__all__'

    def create(self, validated_data):
        eventdata = validated_data.pop('eventdata')
        plannedoperations = validated_data.pop('plannedoperations')
        consumptionconditiondata = validated_data.pop(
            'consumptionconditiondata')

        with transaction.atomic():
            header = ReportHeader.objects.create(**validated_data)
            EventData.objects.create(report_header=header, **eventdata)
            PlannedOperations.objects.create(
                report_header=header, **plannedoperations)

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


class BDNReportViewSerializer(BaseReportViewSerializer):
    bdndata = BDNDataSerializer()

    class Meta:
        model = ReportHeader
        fields = '__all__'

    def create(self, validated_data):
        bdndata = validated_data.pop('bdndata')

        with transaction.atomic():
            header = ReportHeader.objects.create(**validated_data)
            BDNData.objects.create(report_header=header, **bdndata)

        return header
