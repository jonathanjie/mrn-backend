from celery import shared_task

from carboncalc.logic.cii_logic import process_standardized_data_reporting_file
from carboncalc.models import StandardizedDataReportingFile


@shared_task
def process_uploaded_data_report(file_uuid):
    file = StandardizedDataReportingFile.objects.get(uuid=file_uuid)
    process_standardized_data_reporting_file(file)
