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
            leg_fo_robs[fo_type] = str(fuel_oil_data.rob)

            cons_breakdown = fuel_oil_data.breakdown
            if report_header.report_type in (ReportType.DEP_COSP,
                                             ReportType.NOON,
                                             ReportType.ARR_SBY,
                                             ReportType.ARR_FWE):
                # Update values for Port to Port consumption
                _update_fo_consumption(fo_type, cons_breakdown, leg_fo_cons_port_to_port)

            if report_header.report_type in (ReportType.NOON,
                                             ReportType.ARR_SBY):
                # Update values for Pilot to Pilot consumption
                _update_fo_consumption(fo_type, cons_breakdown, leg_fo_cons_pilot_to_pilot)

            if report_header.report_type in (ReportType.EVENT_HARBOUR,
                                             ReportType.EVENT_PORT,
                                             ReportType.NOON_HARBOUR,
                                             ReportType.NOON_PORT):
                # Update values for In Harbour / Port consumption
                _update_fo_consumption(fo_type, cons_breakdown, leg_fo_cons_in_harbour_port)

        leg_lo_robs = leg_data.lube_oil_robs
        for lube_oil_data in ccdata.lubricatingoildata_set.all():
            lo_type = lube_oil_data.lubricating_oil_type
            leg_lo_robs[lo_type] = str(lube_oil_data.rob)

        leg_data.freshwater_rob = ccdata.freshwaterdata.rob

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

        if report_header.report_type == ReportType.DEP_SBY:
            leg_data.distance_standby_to_cosp = dt_data.distance_observed_total

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

    # if 'stoppage_data' in kwargs:
    #     pass

    if 'planned_operations' in kwargs:
        planned_operations = kwargs.pop('planned_operations')
        planned_operations_dict = model_to_dict(planned_operations)
        planned_operations_dict.pop('report_header')
        leg_data.planned_operations = planned_operations_dict


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
                leg_fo_cons_for_type[eng_type] += val
            else:
                leg_fo_cons_for_type[eng_type] = val
