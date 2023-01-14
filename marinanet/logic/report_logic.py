from decimal import Decimal

from django.forms.models import model_to_dict

from marinanet.enums import ReportType
from marinanet.models import VoyageLegData


def update_leg_data(report_header, **kwargs):
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
            leg_data.freshwater_cons_in_harbour_port += \
                ccdata.freshwaterdata.consumed
            leg_data.freshwater_gen_in_harbour_port += \
                ccdata.freshwaterdata.generated
            leg_data.freshwater_receipt_in_harbour_port += \
                ccdata.freshwaterdata.received
            leg_data.freshwater_discharge_in_harbour_port += \
                ccdata.freshwaterdata.discharged

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
            else
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

    # if 'arrival_fwe_time_and_position' in kwargs:
    #     pass

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
