from celery import shared_task

from carboncalc.logic.file_processing_logic import (
    process_standardized_data_reporting_file,
)
from carboncalc.models import StandardizedDataReportingFile


@shared_task()
def process_standardized_data_reporting_file_task(
    file_uuid: str,
):
    file = StandardizedDataReportingFile.objects.get(uuid=file_uuid)
    process_standardized_data_reporting_file(file)
