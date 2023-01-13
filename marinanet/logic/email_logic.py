from django.template.loader import render_to_string

from marinanet.models import ReportHeader
from utils import sendgrid_utils


def send_noon_report_email(
        to_address: str,
        report_header: ReportHeader):

    email_subject = "{} - NOON REPORT - {}".format(
        report_header.voyage_leg.voyage.ship.name,
        report_header.report_date)
    email_context = {
        'report_date': report_header.report_date,
        'report_position': report_header.noonreporttimeandposition.position,
        'weather_notation': report_header.weatherdata.weather_notation,
        'wind_direction': report_header.weatherdata.wind_direction,
        'wind_speed': report_header.weatherdata.wind_speed,
        'sea_direction': report_header.weatherdata.sea_direction,
        'sea_state': report_header.weatherdata.sea_state,
        'arrival_port': report_header.reportroute.arrival_port,
        'arrival_date': report_header.reportroute.arrival_date,
        'distance_observed': report_header.distancetimedata.distance_observed_since_last,
        'distance_to_go': report_header.distancetimedata.distance_to_go,
        'current_speed': report_header.performancedata.speed_since_last,
        'current_rpm': report_header.performancedata.rpm_since_last,
        'average_speed': report_header.performancedata.speed_average,
    }

    email_html = render_to_string(
        'emails/reports/noon_report.html',
        email_context)

    response = sendgrid_utils.send_email(
        to_address,
        email_subject,
        email_html)

    return response
