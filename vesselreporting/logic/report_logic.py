from datetime import datetime
from decimal import Decimal
from typing import Optional

from django.contrib.gis.geos import Point
from django.db import transaction
from django.forms.models import model_to_dict

from vesselreporting.enums import ReportType
from vesselreporting.models.report_models import (
    ActualPerformanceData,
    ArrivalFWETimeAndPosition,
    ArrivalPilotStation,
    ArrivalStandbyTimeAndPosition,
    BDNData,
    CargoOperation,
    ConsumptionConditionData,
    DepartureVesselCondition,
    DeparturePilotStation,
    DepartureRunUp,
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
    ReportEdge,
    ReportHeader,
    ReportRoute,
    SailingPlan,
    StoppageData,
    TotalConsumptionData,
    VoyageLeg,
    VoyageLegData,
    VoyageLegProgress,
    WeatherData,
)


@transaction.atomic
def create_report_header(
    voyage_leg: VoyageLeg,
    report_type: str,
    report_num: int,
    report_date: datetime,
    report_tz: float,
) -> ReportHeader:
    """
    Creates a Report Header object
    * Functions should be written in a similar way to allow for testability
    """
    report_header = ReportHeader.objects.create(
        voyage_leg=voyage_leg,
        report_type=report_type,
        report_num=report_num,
        report_date=report_date,
        report_tz=report_tz,
    )
    return report_header


@transaction.atomic
def create_report_route(
    report_header: ReportHeader,
    departure_port: str,
    departure_date: datetime,
    departure_tz: float,
    arrival_port: str,
    arrival_date: datetime,
    arrival_tz: float,
) -> ReportRoute:
    report_route = ReportRoute.objects.create(
        report_header=report_header,
        departure_port=departure_port,
        departure_date=departure_date,
        departure_tz=departure_tz,
        arrival_port=arrival_port,
        arrival_date=arrival_date,
        arrival_tz=arrival_tz,
    )
    return report_route


@transaction.atomic
def create_departure_vessel_condition(
    report_header: ReportHeader,
    draft_fwd: Decimal,
    draft_mid: Decimal,
    draft_aft: Decimal,
    constant: Decimal,
    gm: Decimal,
    ballast: Decimal,
    displacement: Decimal,
) -> DepartureVesselCondition:
    departure_vessel_condition = DepartureVesselCondition.objects.create(
        report_header=report_header,
        draft_fwd=draft_fwd,
        draft_mid=draft_mid,
        draft_aft=draft_aft,
        constant=constant,
        gm=gm,
        ballast=ballast,
        displacement=displacement,
    )
    return departure_vessel_condition


@transaction.atomic
def create_departure_pilot_station(
    report_header: ReportHeader,
    name: str,
    date: datetime,
    position: Point,
) -> DeparturePilotStation:
    departure_pilot_station = DeparturePilotStation.objects.create(
        report_header=report_header,
        name=name,
        date=date,
        position=position,
    )
    return departure_pilot_station


@transaction.atomic
def create_arrival_pilot_station(
    report_header: ReportHeader,
    name: str,
    date: datetime,
    position: Point,
    draft_fwd: Decimal,
    draft_mid: Decimal,
    draft_aft: Decimal,
) -> ArrivalPilotStation:
    arrival_pilot_station = ArrivalPilotStation.objects.create(
        report_header=report_header,
        name=name,
        date=date,
        position=position,
        draft_fwd=draft_fwd,
        draft_mid=draft_mid,
        draft_aft=draft_aft,
    )
    return arrival_pilot_station


@transaction.atomic
def create_consumption_condition_data(
    report_header: ReportHeader,
    consumption_type: str,
) -> ConsumptionConditionData:
    ccdata = ConsumptionConditionData.objects.create(
        report_header=report_header,
        consumption_type=consumption_type,
    )
    return ccdata


@transaction.atomic
def create_fuel_oil_data(
    ccdata: ConsumptionConditionData,
    fuel_oil_type: str,
    total_consumption: Decimal,
    receipt: Decimal,
    debunkering: Decimal,
    rob: Decimal,
    breakdown: dict[str, Decimal],  # This is a JSON
) -> FuelOilData:
    fo_data = FuelOilData.objects.create(
        ccdata=ccdata,
        fuel_oil_type=fuel_oil_type,
        total_consumption=total_consumption,
        receipt=receipt,
        debunkering=debunkering,
        rob=rob,
        breakdown=breakdown,
    )
    return fo_data


@transaction.atomic
def create_fuel_oil_data_correction(
    fuel_oil_data: FuelOilData,
    correction: Decimal,
    remarks: str,
) -> FuelOilDataCorrection:
    fo_data_correction = FuelOilDataCorrection.objects.create(
        fuel_oil_data=fuel_oil_data,
        correction=correction,
        remarks=remarks,
    )
    return fo_data_correction


@transaction.atomic
def process_fuel_oil_data_set(
    ccdata: ConsumptionConditionData,
    fueloildata_set,
) -> None:
    """
    Processes a Set Fuel Oil Data and its corrections
    """
    for fueloildata in fueloildata_set:
        fueloildatacorrection = fueloildata.pop(
            'fueloildatacorrection', None)
        fo_data = create_fuel_oil_data(
            ccdata=ccdata,
            **fueloildata,
        )
        if fueloildatacorrection:
            create_fuel_oil_data_correction(
                fuel_oil_data=fo_data,
                **fueloildatacorrection,
            )


@transaction.atomic
def create_lubricating_oil_data(
    ccdata: ConsumptionConditionData,
    lubricating_oil_type: str,
    total_consumption: Decimal,
    receipt: Decimal,
    debunkering: Decimal,
    rob: Decimal,
) -> LubricatingOilData:
    lo_data = LubricatingOilData.objects.create(
        ccdata=ccdata,
        lubricating_oil_type=lubricating_oil_type,
        total_consumption=total_consumption,
        receipt=receipt,
        debunkering=debunkering,
        rob=rob,
    )
    return lo_data


@transaction.atomic
def create_lubricating_oil_data_correction(
    lubricating_oil_data: LubricatingOilData,
    correction: Decimal,
    remarks: str,
) -> LubricatingOilDataCorrection:
    lo_data_correction = LubricatingOilDataCorrection.objects.create(
        lubricating_oil_data=lubricating_oil_data,
        correction=correction,
        remarks=remarks,
    )
    return lo_data_correction


@transaction.atomic
def process_lubricating_oil_data_set(
    ccdata: ConsumptionConditionData,
    lubricatingoildata_set,
) -> None:
    for lubricatingoildata in lubricatingoildata_set:
        lubricatingoildatacorrection = lubricatingoildata.pop(
            'lubricatingoildatacorrection', None)
        lo_data = create_lubricating_oil_data(
            ccdata=ccdata,
            **lubricatingoildata,
        )
        if lubricatingoildatacorrection:
            create_lubricating_oil_data_correction(
                lubricating_oil_data=lo_data,
                **lubricatingoildatacorrection,
            )


@transaction.atomic
def create_fresh_water_data(
    ccdata: ConsumptionConditionData,
    consumed: int,
    generated: int,
    received: int,
    discharged: int,
    rob: int,
) -> FreshWaterData:
    fw_data = FreshWaterData.objects.create(
        ccdata=ccdata,
        consumed=consumed,
        generated=generated,
        received=received,
        discharged=discharged,
        rob=rob,
    )
    return fw_data


@transaction.atomic
def create_noon_report_time_and_position(
    report_header: ReportHeader,
    time: datetime,
    timezone: float,
    position: Point,
):
    noon_report_time_and_position = NoonReportTimeAndPosition.objects.create(
        report_header=report_header,
        time=time,
        timezone=timezone,
        position=position,
    )
    return noon_report_time_and_position


@transaction.atomic
def create_weather_data(
    report_header: ReportHeader,
    weather_notation: str,
    visibility: int,
    wind_direction: str,
    wind_speed: Decimal,
    sea_direction: str,
    sea_state: int,
    swell_direction: str,
    swell_scale: int,
    air_pressure: int,
    air_temperature_dry: Decimal,
    air_temperature_wet: Decimal,
    sea_temperature: Decimal,
    ice_condition: str,
) -> WeatherData:
    weather_data = WeatherData.objects.create(
        report_header=report_header,
        weather_notation=weather_notation,
        visibility=visibility,
        wind_direction=wind_direction,
        wind_speed=wind_speed,
        sea_direction=sea_direction,
        sea_state=sea_state,
        swell_direction=swell_direction,
        swell_scale=swell_scale,
        air_pressure=air_pressure,
        air_temperature_dry=air_temperature_dry,
        air_temperature_wet=air_temperature_wet,
        sea_temperature=sea_temperature,
        ice_condition=ice_condition,
    )
    return weather_data


@transaction.atomic
def create_heavy_weather_data(
    report_header: ReportHeader,
    weather_notation: str,
    total_hours: Decimal,
    observed_distance: Decimal,
    fuel_consumption: Decimal,
    wind_direction: str,
    wind_speed: Decimal,
    sea_direction: str,
    sea_state: int,
    remarks: Optional[str],
) -> HeavyWeatherData:
    heavy_weather_data = HeavyWeatherData.objects.create(
        report_header=report_header,
        weather_notation=weather_notation,
        total_hours=total_hours,
        observed_distance=observed_distance,
        fuel_consumption=fuel_consumption,
        wind_direction=wind_direction,
        wind_speed=wind_speed,
        sea_direction=sea_direction,
        sea_state=sea_state,
        remarks=remarks,
    )
    return heavy_weather_data


@transaction.atomic
def create_distance_time_data(
    report_header: ReportHeader,
    hours_since_last: Decimal,
    hours_total: Decimal,
    distance_to_go: Decimal,
    remarks_for_changes: str,
    distance_observed_since_last: Decimal,
    distance_observed_total: Decimal,
    distance_engine_since_last: Decimal,
    distance_engine_total: Decimal,
    revolution_count: int,
    set_rpm: Optional[Decimal],
) -> DistanceTimeData:
    distance_time_data = DistanceTimeData.objects.create(
        report_header=report_header,
        hours_since_last=hours_since_last,
        hours_total=hours_total,
        distance_to_go=distance_to_go,
        remarks_for_changes=remarks_for_changes,
        distance_observed_since_last=distance_observed_since_last,
        distance_observed_total=distance_engine_total,
        distance_engine_since_last=distance_engine_since_last,
        distance_engine_total=distance_engine_total,
        revolution_count=revolution_count,
        set_rpm=set_rpm,
    )
    return distance_time_data


@transaction.atomic
def create_performance_data(
    report_header: ReportHeader,
    speed_since_last: Decimal,
    rpm_since_last: Decimal,
    slip_since_last: Decimal,
    speed_average: Decimal,
    rpm_average: Decimal,
    slip_average: Decimal,
) -> PerformanceData:
    performance_data = PerformanceData.objects.create(
        report_header=report_header,
        speed_since_last=speed_since_last,
        rpm_since_last=rpm_since_last,
        slip_since_last=speed_since_last,
        speed_average=speed_average,
        rpm_average=rpm_average,
        slip_average=slip_average,
    )
    return performance_data


@transaction.atomic
def create_stoppage_data(
    report_header: ReportHeader,
    start_date: datetime,
    reduced_rpm: Decimal,
    position: Point,
    reason: str,
    remarks: str,
    end_date: Optional[datetime] = None,
    duration: Optional[Decimal] = None,
) -> StoppageData:
    stoppage_data = StoppageData.objects.create(
        report_header=report_header,
        start_date=start_date,
        end_date=end_date,
        duration=duration,
        reduced_rpm=reduced_rpm,
        position=position,
        reason=reason,
        remarks=remarks,
    )
    return stoppage_data


@transaction.atomic
def create_cargo_operation(
    report_header: ReportHeader,
    load_condition: str,
    loading: int,
    unloading: int,
    total: int,
    time: Decimal,
) -> CargoOperation:
    cargo_operation = CargoOperation.objects.create(
        report_header=report_header,
        load_condition=load_condition,
        loading=loading,
        unloading=unloading,
        total=total,
        time=time,
    )
    return cargo_operation


@transaction.atomic
def create_departure_run_up(
    report_header: ReportHeader,
    time: datetime,
    timezone: float,
    position: Point,
) -> DepartureRunUp:
    depature_run_up = DepartureRunUp.objects.create(
        report_header=report_header,
        time=time,
        timezone=timezone,
        position=position,
    )
    return depature_run_up


@transaction.atomic
def create_sailing_plan(
    report_header: ReportHeader,
    distance_to_go: Decimal,
    speed: Decimal,
    me_daily_fo_consumption: Decimal,
    me_rpm: Decimal,
) -> SailingPlan:
    sailing_plan = SailingPlan.objects.create(
        report_header=report_header,
        distance_to_go=distance_to_go,
        speed=speed,
        me_daily_fo_consumption=me_daily_fo_consumption,
        me_rpm=me_rpm,
    )
    return sailing_plan


@transaction.atomic
def create_arrival_standby_time_and_position(
    report_header: ReportHeader,
    time: datetime,
    timezone: float,
    position: Point,
) -> ArrivalStandbyTimeAndPosition:
    arrival_standby = ArrivalStandbyTimeAndPosition.objects.create(
        report_header=report_header,
        time=time,
        timezone=timezone,
        position=position,
    )
    return arrival_standby


@transaction.atomic
def create_planned_operations(
    report_header: ReportHeader,
    cargo_operation_berth: bool,
    cargo_operation_stsstb: bool,
    bunkering_debunkering: bool,
    dry_docking: bool,
    crew_change: bool,
    receiving_provisions_spares: bool,
    surveying: bool,
    others: bool,
    waiting: Optional[bool] = False,
    planned_operation_othersdetails: Optional[str] = None,
) -> PlannedOperations:
    planned_operations = PlannedOperations.objects.create(
        report_header=report_header,
        waiting=waiting,
        cargo_operation_berth=cargo_operation_berth,
        cargo_operation_stsstb=cargo_operation_stsstb,
        bunkering_debunkering=bunkering_debunkering,
        dry_docking=dry_docking,
        crew_change=crew_change,
        receiving_provisions_spares=receiving_provisions_spares,
        surveying=surveying,
        others=others,
        planned_operation_othersdetails=planned_operation_othersdetails,
    )
    return planned_operations


@transaction.atomic
def create_actual_performance_data(
    report_header: ReportHeader,
    actual_performance_type: str,
    distance_obs_total: Decimal,
    sailing_time: Decimal,
    displacement: Decimal,
    speed_average: Decimal,
    rpm_average: Decimal,
    me_average_daily_fo_consumption: Decimal,
) -> ActualPerformanceData:
    actual_performance_data = ActualPerformanceData.objects.create(
        report_header=report_header,
        actual_performance_type=actual_performance_type,
        distance_obs_total=distance_obs_total,
        sailing_time=sailing_time,
        displacement=displacement,
        speed_average=speed_average,
        rpm_average=rpm_average,
        me_average_daily_fo_consumption=me_average_daily_fo_consumption,
    )
    return actual_performance_data


@transaction.atomic
def create_arrival_fwe_time_and_position(
    report_header: ReportHeader,
    time: datetime,
    timezone: float,
    position: Point,
    parking_status: str
) -> ArrivalFWETimeAndPosition:
    arrival_fwe = ArrivalFWETimeAndPosition.objects.create(
        report_header=report_header,
        time=time,
        timezone=timezone,
        position=position,
        parking_status=parking_status,
    )
    return arrival_fwe


@transaction.atomic
def create_event_data(
    report_header: ReportHeader,
    time: datetime,
    timezone: float,
    position: Point,
    distance_travelled: int,
    parking_status: str,
) -> EventData:
    event_data = EventData.objects.create(
        report_header=report_header,
        time=time,
        timezone=timezone,
        position=position,
        distance_travelled=distance_travelled,
        parking_status=parking_status,
    )
    return event_data


@transaction.atomic
def create_bdn_data(
    report_header: ReportHeader,
    is_before_arrival: bool,
    bunkering_port: str,
    bunkering_date: datetime,
    bdn_file: list[str],
    delivered_oil_type: str,
    delivered_quantity: Decimal,
    density_15: Decimal,
    viscosity_value: Decimal,
    viscosity_temperature: Decimal,
    flash_point: Decimal,
    sulfur_content: Decimal,
    sample_sealing_marpol: str,
    sample_sealing_ship: str,
    sample_sealing_barge: str,
    alongside_date: datetime,
    hose_connection_date: datetime,
    pump_start_date: datetime,
    pump_stop_date: datetime,
    hose_disconnection_date: datetime,
    slipoff_date: datetime,
    purchaser: str,
    barge_name: str,
    supplier_name: str,
    supplier_address: str,
    supplier_contact: str,
) -> BDNData:
    bdb_data = BDNData.objects.create(
        report_header=report_header,
        is_before_arrival=is_before_arrival,
        bunkering_port=bunkering_port,
        bunkering_date=bunkering_date,
        bdn_file=bdn_file,
        delivered_oil_type=delivered_oil_type,
        delivered_quantity=delivered_quantity,
        density_15=density_15,
        viscosity_value=viscosity_value,
        viscosity_temperature=viscosity_temperature,
        flash_point=flash_point,
        sulfur_content=sulfur_content,
        sample_sealing_marpol=sample_sealing_marpol,
        sample_sealing_ship=sample_sealing_ship,
        sample_sealing_barge=sample_sealing_barge,
        alongside_date=alongside_date,
        hose_connection_date=hose_connection_date,
        pump_start_date=pump_start_date,
        pump_stop_date=pump_stop_date,
        hose_disconnection_date=hose_disconnection_date,
        slipoff_date=slipoff_date,
        purchaser=purchaser,
        barge_name=barge_name,
        supplier_name=supplier_name,
        supplier_address=supplier_address,
        supplier_contact=supplier_contact,
    )
    return bdb_data


@transaction.atomic
def create_total_consumption_data(
    report_header: ReportHeader,
    consumption_type: str,
) -> TotalConsumptionData:
    tcdata = TotalConsumptionData.objects.create(
        report_header=report_header,
        consumption_type=consumption_type,
    )
    return tcdata


@transaction.atomic
def create_fuel_oil_total_consumption_data(
    tcdata: TotalConsumptionData,
    fuel_oil_type: str,
    total_consumption: Decimal,
    receipt: Decimal,
    debunkering: Decimal,
    rob: Decimal,
    breakdown: dict[str, Decimal],  # This is a JSON
) -> FuelOilTotalConsumptionData:
    fo_tc_data = FuelOilTotalConsumptionData.objects.create(
        tcdata=tcdata,
        fuel_oil_type=fuel_oil_type,
        total_consumption=total_consumption,
        receipt=receipt,
        debunkering=debunkering,
        rob=rob,
        breakdown=breakdown,
    )
    return fo_tc_data


@transaction.atomic
def create_fuel_oil_total_consumption_data_correction(
    fuel_oil_tcdata: FuelOilTotalConsumptionData,
    correction: Decimal,
    remarks: str,
) -> FuelOilTotalConsumptionDataCorrection:
    fo_tc_data_correction = FuelOilTotalConsumptionDataCorrection.objects.create(
        fuel_oil_tcdata=fuel_oil_tcdata,
        correction=correction,
        remarks=remarks,
    )
    return fo_tc_data_correction


@transaction.atomic
def process_fuel_oil_total_consumption_data_set(
    tcdata: TotalConsumptionData,
    fueloiltotalconsumptiondata_set,
) -> None:
    for fueloiltotalconsumptiondata in fueloiltotalconsumptiondata_set:
        fueloiltotalconsumptiondatacorrection = fueloiltotalconsumptiondata.pop(
            'fueloiltotalconsumptiondatacorrection', None)
        fo_tcdata = create_fuel_oil_total_consumption_data(
            tcdata=tcdata,
            **fueloiltotalconsumptiondata
        )
        if fueloiltotalconsumptiondatacorrection:
            create_fuel_oil_total_consumption_data_correction(
                fuel_oil_tcdata=fo_tcdata,
                **fueloiltotalconsumptiondatacorrection
            )


@transaction.atomic
def create_lubricating_oil_total_consumption_data(
    tcdata: TotalConsumptionData,
    lubricating_oil_type: str,
    total_consumption: Decimal,
    receipt: Decimal,
    debunkering: Decimal,
    rob: Decimal,
) -> LubricatingOilTotalConsumptionData:
    lo_tc_data = LubricatingOilTotalConsumptionData.objects.create(
        tcdata=tcdata,
        lubricating_oil_type=lubricating_oil_type,
        total_consumption=total_consumption,
        receipt=receipt,
        debunkering=debunkering,
        rob=rob,
    )
    return lo_tc_data


@transaction.atomic
def create_lubricating_oil_total_consumption_data_correction(
    lubricating_oil_tcdata: LubricatingOilTotalConsumptionData,
    correction: Decimal,
    remarks: str,
) -> LubricatingOilTotalConsumptionDataCorrection:
    lo_tc_data_correction = LubricatingOilTotalConsumptionDataCorrection.objects.create(
        lubricating_oil_tcdata=lubricating_oil_tcdata,
        correction=correction,
        remarks=remarks,
    )
    return lo_tc_data_correction


@transaction.atomic
def process_lubricating_oil_total_consumption_data_set(
    tcdata: TotalConsumptionData,
    lubricatingoiltotalconsumptiondata_set,
) -> None:
    for lubricatingoiltotalconsumptiondata in lubricatingoiltotalconsumptiondata_set:
        lubricatingoiltotalconsumptiondatacorrection = lubricatingoiltotalconsumptiondata.pop(
            'lubricatingoiltotalconsumptiondatacorrection', None)
        lo_tcdata = create_lubricating_oil_total_consumption_data(
            tcdata=tcdata, **lubricatingoiltotalconsumptiondata)
        if lubricatingoiltotalconsumptiondatacorrection:
            create_lubricating_oil_total_consumption_data_correction(
                lubricating_oil_tcdata=lo_tcdata,
                **lubricatingoiltotalconsumptiondatacorrection)


@transaction.atomic
def create_fresh_water_total_consumption_data(
    tcdata: TotalConsumptionData,
    consumed: int,
    generated: int,
    received: int,
    discharged: int,
    rob: int,
) -> FreshWaterTotalConsumptionData:
    fw_tc_data = FreshWaterTotalConsumptionData.objects.create(
        tcdata=tcdata,
        consumed=consumed,
        generated=generated,
        received=received,
        discharged=discharged,
        rob=rob,
    )
    return fw_tc_data


@transaction.atomic
def update_leg_data(report_header, **kwargs):
    """
    This function updates data that is carried over from report to report
    """
    voyage_leg = report_header.voyage_leg
    leg_data, created = VoyageLegData.objects.get_or_create(
        voyage_leg=voyage_leg)
    if created:
        leg_data.propeller_pitch = voyage_leg.voyage.ship.\
            shipspecs.propeller_pitch

    leg_data.last_report_type = report_header.report_type
    leg_data.last_report_date = report_header.report_date

    if 'report_route' in kwargs:
        route = kwargs.pop('report_route')
        leg_data.departure_port = route.departure_port
        leg_data.departure_date = route.departure_date
        leg_data.departure_tz = route.departure_tz
        leg_data.arrival_port = route.arrival_port
        leg_data.arrival_date = route.arrival_date
        leg_data.arrival_tz = route.arrival_tz

    if 'cargo_operation' in kwargs:
        cargo_operation = kwargs.pop('cargo_operation')
        leg_data.load_condition = cargo_operation.load_condition
        leg_data.cargo_total_at_departure = cargo_operation.total

    if 'departure_condition' in kwargs:
        dep_condition = kwargs.pop('departure_condition')
        leg_data.displacement_at_departure = dep_condition.displacement

    if 'consumption_condition_data' in kwargs:
        ccdata = kwargs.pop('consumption_condition_data')
        leg_fo_robs = leg_data.fuel_oil_robs
        leg_fo_cons_port_to_port = leg_data.fuel_oil_cons_port_to_port
        leg_fo_cons_pilot_to_pilot = leg_data.fuel_oil_cons_pilot_to_pilot
        leg_fo_cons_in_harbour_port = leg_data.fuel_oil_cons_in_harbour_port

        for fuel_oil_data in ccdata.fueloildata_set.all():
            fo_type = fuel_oil_data.fuel_oil_type
            leg_fo_robs[fo_type] = fuel_oil_data.rob

            cons_breakdown = fuel_oil_data.breakdown
            if report_header.report_type in (ReportType.DEP_COSP,
                                             ReportType.NOON,
                                             ReportType.ARR_SBY,
                                             ReportType.ARR_FWE):
                # Update values for Port to Port consumption
                _update_fo_consumption(
                    fo_type,
                    cons_breakdown,
                    leg_fo_cons_port_to_port)

            if report_header.report_type in (ReportType.NOON,
                                             ReportType.ARR_SBY):
                # Update values for Pilot to Pilot consumption
                _update_fo_consumption(
                    fo_type,
                    cons_breakdown,
                    leg_fo_cons_pilot_to_pilot)

            if report_header.report_type in (ReportType.EVENT_HARBOUR,
                                             ReportType.EVENT_PORT,
                                             ReportType.NOON_HARBOUR,
                                             ReportType.NOON_PORT):
                # Update values for In Harbour / Port consumption
                _update_fo_consumption(
                    fo_type,
                    cons_breakdown,
                    leg_fo_cons_in_harbour_port)
                _update_oil_dict(
                    fo_type,
                    fuel_oil_data.receipt,
                    leg_data.fuel_oil_receipt_in_harbour_port)
                _update_oil_dict(
                    fo_type,
                    fuel_oil_data.debunkering,
                    leg_data.fuel_oil_debunker_in_harbour_port)

        leg_lo_robs = leg_data.lube_oil_robs
        for lube_oil_data in ccdata.lubricatingoildata_set.all():
            lo_type = lube_oil_data.lubricating_oil_type
            leg_lo_robs[lo_type] = lube_oil_data.rob

            if report_header.report_type in (ReportType.EVENT_HARBOUR,
                                             ReportType.EVENT_PORT,
                                             ReportType.NOON_HARBOUR,
                                             ReportType.NOON_PORT):
                _update_oil_dict(
                    lo_type,
                    lube_oil_data.total_consumption,
                    leg_data.lube_oil_cons_in_harbour_port)
                _update_oil_dict(
                    lo_type,
                    lube_oil_data.receipt,
                    leg_data.lube_oil_receipt_in_harbour_port)
                _update_oil_dict(
                    lo_type,
                    lube_oil_data.debunkering,
                    leg_data.lube_oil_debunker_in_harbour_port)

        leg_data.freshwater_rob = ccdata.freshwaterdata.rob
        if report_header.report_type in (ReportType.EVENT_HARBOUR,
                                         ReportType.EVENT_PORT,
                                         ReportType.NOON_HARBOUR,
                                         ReportType.NOON_PORT):
            leg_data.freshwater_cons_in_harbour_port += ccdata.freshwaterdata.consumed
            leg_data.freshwater_gen_in_harbour_port += ccdata.freshwaterdata.generated
            leg_data.freshwater_receipt_in_harbour_port += ccdata.freshwaterdata.received
            leg_data.freshwater_discharge_in_harbour_port += ccdata.freshwaterdata.discharged

    # if 'total_consumption_data' in kwargs:
    #     pass

    # if 'departure_pilot_station' in kwargs:
    #     pass

    # if 'arrival_pilot_station' in kwargs:
    #     pass

    # if 'departure_runup' in kwargs:
    #     pass

    if 'distance_time_data' in kwargs:
        dt_data = kwargs.pop('distance_time_data')
        leg_data.total_hours = dt_data.hours_total
        leg_data.distance_observed_total = dt_data.distance_observed_total
        leg_data.distance_engine_total = dt_data.distance_engine_total
        leg_data.revolution_count = dt_data.revolution_count
        leg_data.distance_to_go = dt_data.distance_to_go

        if report_header.report_type == ReportType.DEP_COSP:
            leg_data.distance_obs_standby_to_cosp = \
                dt_data.distance_observed_since_last
            leg_data.distance_eng_standby_to_cosp = \
                dt_data.distance_engine_since_last
            leg_data.time_standby_to_cosp = dt_data.hours_since_last
            leg_data.revolution_count_standby_to_cosp = \
                dt_data.revolution_count

    if 'sailing_plan' in kwargs:
        sailing_plan = kwargs.pop('sailing_plan')
        leg_data.distance_to_go = sailing_plan.distance_to_go

    # if 'noon_report_time_and_position' in kwargs:
    #     pass

    # if 'weather_data' in kwargs:
    #     pass

    # if 'heavy_weather_data' in kwargs:
    #     pass

    if 'performance_data' in kwargs:
        performance_data = kwargs.pop('performance_data')
        leg_data.speed_average = performance_data.speed_average
        leg_data.rpm_average = performance_data.rpm_average
        leg_data.slip_average = performance_data.slip_average

    if 'stoppage_data' in kwargs:
        stoppage_data = kwargs.pop('stoppage_data')
        if stoppage_data.reduced_rpm == 0 and stoppage_data.duration:
            if leg_data.time_stopped_at_sea:
                leg_data.time_stopped_at_sea += stoppage_data.duration
            else:
                leg_data.time_stopped_at_sea = stoppage_data.duration

    if 'planned_operations' in kwargs:
        planned_operations = kwargs.pop('planned_operations')
        planned_operations_dict = model_to_dict(planned_operations)
        planned_operations_dict.pop('report_header')

        if report_header.report_type == ReportType.ARR_SBY:
            leg_data.planned_operations = planned_operations_dict

        if report_header.report_type in (ReportType.EVENT_HARBOUR,
                                         ReportType.EVENT_PORT,
                                         ReportType.NOON_HARBOUR,
                                         ReportType.NOON_PORT):
            leg_data.last_operation = planned_operations_dict

    # if 'arrival_standby_time_and_position' in kwargs:
    #     pass

    if 'arrival_fwe_time_and_position' in kwargs:
        arrfwe_data = kwargs.pop('arrival_fwe_time_and_position')
        leg_data.parking_status = arrfwe_data.parking_status

    if 'event_data' in kwargs:
        event_data = kwargs.pop('event_data')
        leg_data.parking_status = event_data.parking_status

    # if 'bdn_data' in kwargs:
    #     pass

    leg_data.save()
    return leg_data


def _update_fo_consumption(fo_type, cons_breakdown_dict, leg_fo_cons_dict):
    if fo_type not in leg_fo_cons_dict:
        leg_fo_cons_dict[fo_type] = cons_breakdown_dict
    else:
        leg_fo_cons_for_type = leg_fo_cons_dict[fo_type]
        for eng_type, val in cons_breakdown_dict.items():
            if eng_type in leg_fo_cons_for_type:
                leg_fo_cons_for_type[eng_type] = \
                    Decimal(leg_fo_cons_for_type[eng_type]) + Decimal(val)
            else:
                leg_fo_cons_for_type[eng_type] = val


def _update_oil_dict(oil_type, new_val, update_dict):
    if oil_type in update_dict:
        curr_val = update_dict[oil_type]
        update_dict[oil_type] = Decimal(curr_val) + new_val
    else:
        update_dict[oil_type] = new_val
    return update_dict


@transaction.atomic
def update_leg_progress(report_header):
    leg_progress = report_header.voyage_leg.voyagelegprogress

    previous_report = leg_progress.latest_report
    if not previous_report:
        # CASE: This report is first in the voyage
        last_legs = VoyageLeg.objects.filter(
            voyage__ship=report_header.voyage_leg.voyage.ship,
        ).select_related(
            'voyagelegprogress',
        ).order_by('-created_at')[:2]
        if len(last_legs) == 2:
            previous_report = last_legs[1].voyagelegprogress.latest_report

    ReportEdge.objects.update_or_create(
        previous_report=previous_report,
        defaults={'next_report': report_header},
    )

    leg_progress.latest_report = report_header
    if report_header.report_type == ReportType.DEP_SBY:
        assert(leg_progress.departure_standby is None)
        leg_progress.departure_standby = report_header
    elif report_header.report_type == ReportType.DEP_COSP:
        assert(leg_progress.departure_cosp is None)
        leg_progress.departure_cosp = report_header
    elif report_header.report_type == ReportType.NOON:
        leg_progress.latest_noon = report_header
    elif report_header.report_type == ReportType.ARR_SBY:
        assert(leg_progress.arrival_ is None)
        leg_progress.arrival_eosp = report_header
    elif report_header.report_type == ReportType.ARR_FWE:
        assert(leg_progress.arrival_fwe is None)
        leg_progress.arrival_fwe = report_header
    leg_progress.save()



@transaction.atomic
def create_noon_report(
    reportheader,
    reportroute,
    noonreporttimeandposition,
    weatherdata,
    distancetimedata,
    performancedata,
    consumptionconditiondata,
    heavyweatherdata=None,
    stoppagedata=None
) -> ReportHeader:
    header = create_report_header(**reportheader)
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
    update_leg_progress(header)
    return header


@transaction.atomic
def create_departure_standby_report(
    reportheader,
    reportroute,
    cargooperation,
    departurevesselcondition,
    consumptionconditiondata,
    totalconsumptiondata,
    departurepilotstation=None,
) -> ReportHeader:
    header = create_report_header(**reportheader)
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
    update_leg_progress(header)
    return header


@transaction.atomic
def create_departure_cosp_report(
    reportheader,
    reportroute,
    departurerunup,
    distancetimedata,
    sailingplan,
    consumptionconditiondata,
    departurepilotstation=None,
    arrivalpilotstation=None,
) -> ReportHeader:
    header = create_report_header(**reportheader)
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
    update_leg_progress(header)
    return header


@transaction.atomic
def create_arrival_standby_report(
    reportheader,
    reportroute,
    plannedoperations,
    arrivalstandbytimeandposition,
    weatherdata,
    distancetimedata,
    performancedata,
    consumptionconditiondata,
    actualperformancedata,
    totalconsumptiondata,
    arrivalpilotstation=None,
) -> ReportHeader:
    header = create_report_header(**reportheader)
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
    update_leg_progress(header)
    return header


@transaction.atomic
def create_arrival_fwe_report(
    reportheader,
    reportroute,
    arrivalfwetimeandposition,
    plannedoperations,
    distancetimedata,
    consumptionconditiondata,
    actualperformancedata,
    totalconsumptiondata,
    arrivalpilotstation=None,
) -> ReportHeader:
    header = create_report_header(**reportheader)
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
    update_leg_progress(header)
    return header


@transaction.atomic
def create_event_report(
    reportheader,
    eventdata,
    plannedoperations,
    consumptionconditiondata,
) -> ReportHeader:
    header = create_report_header(**reportheader)
    event_data=create_event_data(report_header=header, **eventdata)
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
        event_data=event_data,
        planned_operations=planned_operations,
        consumption_condition_data=ccdata,
    )
    update_leg_progress(header)
    return header


@transaction.atomic
def create_bdn_report(
    reportheader,
    bdndata,
) -> ReportHeader:
    header = create_report_header(**reportheader)
    create_bdn_data(report_header=header, **bdndata)

    leg_data = update_leg_data(
        report_header=header,
    )
    update_leg_progress(header)
    return header
