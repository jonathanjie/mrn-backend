from django.db import transaction
from rest_framework import serializers

from marinanet.models.report_models import (
    BDNData,
    FreshWaterTotalConsumptionData,
    FuelOilTotalConsumptionData,
    FuelOilTotalConsumptionDataCorrection,
    LubricatingOilTotalConsumptionData,
    LubricatingOilTotalConsumptionDataCorrection,
    ReportHeader,
    TotalConsumptionData,
    VoyageLeg,
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
from marinanet.logic.report_logic import (
    create_actual_performance_data,
    create_arrival_fwe_time_and_position,
    create_arrival_pilot_station,
    create_arrival_standby_time_and_position,
    create_bdn_data,
    create_cargo_operation,
    create_consumption_condition_data,
    create_departure_pilot_station,
    create_departure_run_up,
    create_departure_vessel_condition,
    create_distance_time_data,
    create_event_data,
    create_fresh_water_data,
    create_fresh_water_total_consumption_data,
    create_heavy_weather_data,
    create_noon_report_time_and_position,
    create_performance_data,
    create_planned_operations,
    create_report_header,
    create_report_route,
    create_sailing_plan,
    create_stoppage_data,
    create_total_consumption_data,
    create_weather_data,
    process_fuel_oil_data_set,
    process_fuel_oil_total_consumption_data_set,
    process_lubricating_oil_data_set,
    process_lubricating_oil_total_consumption_data_set,
    update_leg_data,
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
            header = create_report_header(**validated_data)
            report_route = create_report_route(
                report_header=header, **reportroute)
            noon_report_time_and_position = create_noon_report_time_and_position(
                report_header=header, **noonreporttimeandposition)
            create_weather_data(report_header=header, **weatherdata)
            if heavyweatherdata:
                create_heavy_weather_data(
                    report_header=header, **heavyweatherdata)
            distance_time_data = create_distance_time_data(
                report_header=header, **distancetimedata)
            performance_data = create_performance_data(
                report_header=header, **performancedata)
            if stoppagedata:
                stoppage_data = create_stoppage_data(
                    report_header=header, **stoppagedata)

            fueloildata_set = consumptionconditiondata.pop('fueloildata_set')
            lubricatingoildata_set = consumptionconditiondata.pop(
                'lubricatingoildata_set')
            freshwaterdata = consumptionconditiondata.pop(
                'freshwaterdata')

            ccdata = create_consumption_condition_data(
                report_header=header, **consumptionconditiondata)
            process_fuel_oil_data_set(ccdata, fueloildata_set)
            process_lubricating_oil_data_set(ccdata, lubricatingoildata_set)
            create_fresh_water_data(ccdata=ccdata, **freshwaterdata)

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
            header = create_report_header(**validated_data)
            report_route = create_report_route(
                report_header=header, **reportroute)
            cargo_operation = create_cargo_operation(
                report_header=header, **cargooperation)
            departure_condition = create_departure_vessel_condition(
                report_header=header, **departurevesselcondition)
            if departurepilotstation:
                create_departure_pilot_station(
                    report_header=header, **departurepilotstation)

            fueloildata_set = consumptionconditiondata.pop('fueloildata_set')
            lubricatingoildata_set = consumptionconditiondata.pop(
                'lubricatingoildata_set')
            freshwaterdata = consumptionconditiondata.pop(
                'freshwaterdata')
            ccdata = create_consumption_condition_data(
                report_header=header, **consumptionconditiondata)
            process_fuel_oil_data_set(ccdata, fueloildata_set)
            process_lubricating_oil_data_set(ccdata, lubricatingoildata_set)
            create_fresh_water_data(ccdata=ccdata, **freshwaterdata)

            fueloiltotalconsumptiondata_set = totalconsumptiondata.pop(
                'fueloiltotalconsumptiondata_set')
            lubricatingoiltotalconsumptiondata_set = totalconsumptiondata.pop(
                'lubricatingoiltotalconsumptiondata_set')
            freshwatertotalconsumptiondata = totalconsumptiondata.pop(
                'freshwatertotalconsumptiondata')

            tcdata = create_total_consumption_data(
                report_header=header, **totalconsumptiondata)
            process_fuel_oil_total_consumption_data_set(
                tcdata, fueloiltotalconsumptiondata_set)
            process_lubricating_oil_total_consumption_data_set(
                tcdata, lubricatingoiltotalconsumptiondata_set)
            create_fresh_water_total_consumption_data(
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
            header = create_report_header(**validated_data)
            report_route = create_report_route(
                report_header=header, **reportroute)
            if departurepilotstation:
                create_departure_pilot_station(
                    report_header=header, **departurepilotstation)
            if arrivalpilotstation:
                create_arrival_pilot_station(
                    report_header=header, **arrivalpilotstation)
            create_departure_run_up(
                report_header=header, **departurerunup)
            distance_time_data = create_distance_time_data(
                report_header=header, **distancetimedata)
            sailing_plan = create_sailing_plan(
                report_header=header, **sailingplan)

            fueloildata_set = consumptionconditiondata.pop('fueloildata_set')
            lubricatingoildata_set = consumptionconditiondata.pop(
                'lubricatingoildata_set')
            freshwaterdata = consumptionconditiondata.pop(
                'freshwaterdata')

            ccdata = create_consumption_condition_data(
                report_header=header, **consumptionconditiondata)
            process_fuel_oil_data_set(ccdata, fueloildata_set)
            process_lubricating_oil_data_set(ccdata, lubricatingoildata_set)
            create_fresh_water_data(ccdata=ccdata, **freshwaterdata)

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
            header = create_report_header(**validated_data)
            report_route = create_report_route(
                report_header=header, **reportroute)
            planned_operations = create_planned_operations(
                report_header=header, **plannedoperations)
            create_arrival_standby_time_and_position(
                report_header=header, **arrivalstandbytimeandposition)
            create_weather_data(report_header=header, **weatherdata)
            distance_time_data = create_distance_time_data(
                report_header=header, **distancetimedata)
            performance_data = create_performance_data(
                report_header=header, **performancedata)
            if arrivalpilotstation:
                create_arrival_pilot_station(
                    report_header=header, **arrivalpilotstation)

            fueloildata_set = consumptionconditiondata.pop('fueloildata_set')
            lubricatingoildata_set = consumptionconditiondata.pop(
                'lubricatingoildata_set')
            freshwaterdata = consumptionconditiondata.pop(
                'freshwaterdata')

            ccdata = create_consumption_condition_data(
                report_header=header, **consumptionconditiondata)
            process_fuel_oil_data_set(ccdata, fueloildata_set)
            process_lubricating_oil_data_set(ccdata, lubricatingoildata_set)
            create_fresh_water_data(ccdata=ccdata, **freshwaterdata)

            create_actual_performance_data(
                report_header=header, **actualperformancedata)

            fueloiltotalconsumptiondata_set = totalconsumptiondata.pop(
                'fueloiltotalconsumptiondata_set')

            # Arrival Standby Total Consumption should not have
            # lubricating oil or freshwater
            lubricatingoiltotalconsumptiondata_set = totalconsumptiondata.pop(
                'lubricatingoiltotalconsumptiondata_set', None)
            freshwatertotalconsumptiondata = totalconsumptiondata.pop(
                'freshwatertotalconsumptiondata', None)

            tcdata = create_total_consumption_data(
                report_header=header, **totalconsumptiondata)
            process_fuel_oil_total_consumption_data_set(
                tcdata, fueloiltotalconsumptiondata_set)

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
            header = create_report_header(**validated_data)
            report_route = create_report_route(
                report_header=header, **reportroute)
            arrival_fwe = create_arrival_fwe_time_and_position(
                report_header=header, **arrivalfwetimeandposition)
            planned_operations = create_planned_operations(
                report_header=header, **plannedoperations)
            if arrivalpilotstation:
                create_arrival_pilot_station(
                    report_header=header, **arrivalpilotstation)
            distance_time_data = create_distance_time_data(
                report_header=header, **distancetimedata)

            fueloildata_set = consumptionconditiondata.pop('fueloildata_set')
            lubricatingoildata_set = consumptionconditiondata.pop(
                'lubricatingoildata_set')
            freshwaterdata = consumptionconditiondata.pop(
                'freshwaterdata')

            ccdata = create_consumption_condition_data(
                report_header=header, **consumptionconditiondata)
            process_fuel_oil_data_set(ccdata, fueloildata_set)
            process_lubricating_oil_data_set(ccdata, lubricatingoildata_set)
            create_fresh_water_data(ccdata=ccdata, **freshwaterdata)

            create_actual_performance_data(
                report_header=header, **actualperformancedata)

            fueloiltotalconsumptiondata_set = totalconsumptiondata.pop(
                'fueloiltotalconsumptiondata_set')

            # Arrival FWE Total Consumption should not have
            # lubricating oil or freshwater
            lubricatingoiltotalconsumptiondata_set = totalconsumptiondata.pop(
                'lubricatingoiltotalconsumptiondata_set', None)
            freshwatertotalconsumptiondata = totalconsumptiondata.pop(
                'freshwatertotalconsumptiondata', None)

            tcdata = create_total_consumption_data(
                report_header=header, **totalconsumptiondata)
            process_fuel_oil_total_consumption_data_set(
                tcdata, fueloiltotalconsumptiondata_set)

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

    def create(self, validated_data) -> ReportHeader:
        eventdata = validated_data.pop('eventdata')
        plannedoperations = validated_data.pop('plannedoperations')
        consumptionconditiondata = validated_data.pop(
            'consumptionconditiondata')

        with transaction.atomic():
            header = create_report_header(**validated_data)
            create_event_data(report_header=header, **eventdata)
            planned_operations = create_planned_operations(
                report_header=header, **plannedoperations)

            fueloildata_set = consumptionconditiondata.pop('fueloildata_set')
            lubricatingoildata_set = consumptionconditiondata.pop(
                'lubricatingoildata_set')
            freshwaterdata = consumptionconditiondata.pop(
                'freshwaterdata')

            ccdata = create_consumption_condition_data(
                report_header=header, **consumptionconditiondata)
            process_fuel_oil_data_set(ccdata, fueloildata_set)
            process_lubricating_oil_data_set(ccdata, lubricatingoildata_set)
            create_fresh_water_data(ccdata=ccdata, **freshwaterdata)

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

    def create(self, validated_data) -> ReportHeader:
        bdndata = validated_data.pop('bdndata')

        with transaction.atomic():
            header = create_report_header(**validated_data)
            create_bdn_data(report_header=header, **bdndata)

            leg_data = update_leg_data(
                report_header=header,
            )

        return header
