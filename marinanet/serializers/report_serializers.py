from django.db import transaction
from rest_framework import serializers

from marinanet.models.report_models import (
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
from marinanet.logic.report_logic import update_leg_data


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

    def create(self, validated_data):
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
            header = ReportHeader.objects.create(**validated_data)
            report_route = ReportRoute.objects.create(
                report_header=header, **reportroute)
            noon_report_time_and_position = NoonReportTimeAndPosition.objects.create(
                report_header=header, **noonreporttimeandposition)
            WeatherData.objects.create(report_header=header, **weatherdata)
            if heavyweatherdata:
                HeavyWeatherData.objects.create(
                    report_header=header, **heavyweatherdata)
            distance_time_data = DistanceTimeData.objects.create(
                report_header=header, **distancetimedata)
            performance_data = PerformanceData.objects.create(
                report_header=header, **performancedata)
            if stoppagedata:
                stoppage_data = StoppageData.objects.create(
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

            leg_data_dict = {
                'report_route': report_route,
                'distance_time_data': distance_time_data,
                'performance_data': performance_data,
                'consumption_condition_data': ccdata,
            }
            if stoppagedata:
                leg_data_dict['stoppage_data'] = stoppage_data
            leg_data = update_leg_data(header, **leg_data_dict)

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
            header = ReportHeader.objects.create(**validated_data)
            report_route = ReportRoute.objects.create(
                report_header=header, **reportroute)
            cargo_operation = CargoOperation.objects.create(
                report_header=header, **cargooperation)
            departure_condition = DepartureVesselCondition.objects.create(
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

            leg_data = update_leg_data(
                report_header=header,
                report_route=report_route,
                cargo_operation=cargo_operation,
                departure_condition=departure_condition,
                consumption_condition_data=ccdata,
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

    def create(self, validated_data):
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
            header = ReportHeader.objects.create(**validated_data)
            report_route = ReportRoute.objects.create(
                report_header=header, **reportroute)
            if departurepilotstation:
                DeparturePilotStation.objects.create(
                    report_header=header, **departurepilotstation)
            if arrivalpilotstation:
                ArrivalPilotStation.objects.create(
                    report_header=header, **arrivalpilotstation)
            DepartureRunUp.objects.create(
                report_header=header, **departurerunup)
            distance_time_data = DistanceTimeData.objects.create(
                report_header=header, **distancetimedata)
            sailing_plan = SailingPlan.objects.create(
                report_header=header, **sailingplan)

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

            leg_data = update_leg_data(
                report_header=header,
                report_route=report_route,
                distance_time_data=distance_time_data,
                sailing_plan=sailing_plan,
                consumption_condition_data=ccdata,
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

    def create(self, validated_data):
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
            header = ReportHeader.objects.create(**validated_data)
            report_route = ReportRoute.objects.create(
                report_header=header, **reportroute)
            planned_operations = PlannedOperations.objects.create(
                report_header=header, **plannedoperations)
            ArrivalStandbyTimeAndPosition.objects.create(
                report_header=header, **arrivalstandbytimeandposition)
            WeatherData.objects.create(report_header=header, **weatherdata)
            distance_time_data = DistanceTimeData.objects.create(
                report_header=header, **distancetimedata)
            performance_data = PerformanceData.objects.create(
                report_header=header, **performancedata)
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

            # Arrival Standby Total Consumption should not have
            # lubricating oil or freshwater
            lubricatingoiltotalconsumptiondata_set = totalconsumptiondata.pop(
                'lubricatingoiltotalconsumptiondata_set', None)
            freshwatertotalconsumptiondata = totalconsumptiondata.pop(
                'freshwatertotalconsumptiondata', None)

            tcdata = TotalConsumptionData.objects.create(
                report_header=header, **totalconsumptiondata)
            for fueloiltotalconsumptiondata in fueloiltotalconsumptiondata_set:
                fo_tcdata = FuelOilTotalConsumptionData.objects.create(
                    tcdata=tcdata, **fueloiltotalconsumptiondata)

            leg_data = update_leg_data(
                report_header=header,
                report_route=report_route,
                planned_operations=planned_operations,
                distance_time_data=distance_time_data,
                performance_data=performance_data,
                consumption_condition_data=ccdata,
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

    def create(self, validated_data):
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
            header = ReportHeader.objects.create(**validated_data)
            report_route = ReportRoute.objects.create(
                report_header=header, **reportroute)
            arrival_fwe = ArrivalFWETimeAndPosition.objects.create(
                report_header=header, **arrivalfwetimeandposition)
            planned_operations = PlannedOperations.objects.create(
                report_header=header, **plannedoperations)
            if arrivalpilotstation:
                ArrivalPilotStation.objects.create(
                    report_header=header, **arrivalpilotstation)
            distance_time_data = DistanceTimeData.objects.create(
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

            # Arrival FWE Total Consumption should not have
            # lubricating oil or freshwater
            lubricatingoiltotalconsumptiondata_set = totalconsumptiondata.pop(
                'lubricatingoiltotalconsumptiondata_set', None)
            freshwatertotalconsumptiondata = totalconsumptiondata.pop(
                'freshwatertotalconsumptiondata', None)

            tcdata = TotalConsumptionData.objects.create(
                report_header=header, **totalconsumptiondata)
            for fueloiltotalconsumptiondata in fueloiltotalconsumptiondata_set:
                fo_tcdata = FuelOilTotalConsumptionData.objects.create(
                    tcdata=tcdata, **fueloiltotalconsumptiondata)

            leg_data = update_leg_data(
                report_header=header,
                arrival_fwe_time_and_position=arrival_fwe,
                planned_operations=planned_operations,
                consumption_condition_data=ccdata,
                distance_time_data=distance_time_data,
            )

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
            planned_operations = PlannedOperations.objects.create(
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

            leg_data = update_leg_data(
                report_header=header,
                event_data=eventdata,
                planned_operations=planned_operations,
                consumption_condition_data=ccdata,
            )

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

            leg_data = update_leg_data(
                report_header=header,
            )

        return header
