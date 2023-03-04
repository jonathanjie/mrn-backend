from celery import shared_task

from carboncalc.enums import FileAcceptanceStatus
from carboncalc.logic.cii_logic import (
    populate_boundaries_for_ship,
    process_cii_raw_data,
)
from carboncalc.logic.file_processing_logic import (
    process_standardized_data_reporting_file,
)
from carboncalc.models import (
    CIIRawData,
    StandardizedDataReportingData,
    StandardizedDataReportingFile,
)
from core.models import Ship


@shared_task()
def process_standardized_data_reporting_file_task(
    file_uuid: str,
):
    file = StandardizedDataReportingFile.objects.get(uuid=file_uuid)
    file_data = process_standardized_data_reporting_file(file)
    file.acceptance_status = FileAcceptanceStatus.ACCEPTED
    file.save()
    generate_cii_raw_data_from_reporting_file_data.delay(
        file_data_uuid=file_data.uuid)


@shared_task()
def generate_cii_raw_data_from_reporting_file_data(
    file_data_uuid: str,
):
    file_data = StandardizedDataReportingData.objects.get(uuid=file_data_uuid)
    cii_raw_data, _ = CIIRawData.objects.update_or_create(
        ship=file_data.ship,
        year=file_data.year,
        defaults={
            'start_date': file_data.start_date,
            'end_date': file_data.end_date,
            'distance_sailed': file_data.total_distance,
            'fuel_oil_burned': file_data.fuel_oil_burned,
        }
    )
    calculate_cii_from_raw_data_task.delay(raw_cii_data_uuid=cii_raw_data.uuid)


@shared_task
def calculate_cii_from_raw_data_task(
    raw_cii_data_uuid: str,
):
    raw_cii = CIIRawData.objects.get(uuid=raw_cii_data_uuid)
    process_cii_raw_data(raw_cii)



@shared_task()
def populate_cii_boundaries_for_ship_task(
    ship_imo: int,
):
    ship = Ship.objects.get(imo_reg=ship_imo)
    populate_boundaries_for_ship(ship)
