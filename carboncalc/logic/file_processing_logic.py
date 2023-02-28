import requests

from carboncalc.enums import (
    CIIFuelType,
)
from carboncalc.models import (
    StandardizedDataReportingData,
    StandardizedDataReportingFile,
)
from core.models import Ship
from utils.filetype_utils import get_file_extension


PDF_DATA_REPORTING_LAMBDA = "https://neapj5jo27o6a22mxs7lkb56ny0jiuzu.lambda-url.ap-southeast-1.on.aws/"
XLSX_DATA_REPORTING_LAMBDA = "https://ykmupploq5r6j5ws3jqb5g76yi0zcqwu.lambda-url.ap-southeast-1.on.aws/"


def process_standardized_data_reporting_file(
    data_report: StandardizedDataReportingFile,
):
    file_extension = get_file_extension(data_report.s3_file_path)
    filepath = {
        'filepath': data_report.s3_file_path,
    }
    if file_extension == ".pdf":
        response = requests.post(
            PDF_DATA_REPORTING_LAMBDA,
            json=filepath,
        )
        json_response = response.json()
        data = json_response.get('data')

        start_date = data["Start date for DCS"]
        end_date = data["End date for DCS"]
        gross_tonnage = data["Gross tonnage"]
        deadweight_tonnage = data["DWT"]
        total_hours = data["Hours underway (h)"]
        total_distance = data["Distance Travelled (nm)"]
        fuel_oil_burned = _process_fuel_types_for_pdf(
            data["Fuel oil consumption(t)"])
    else:
        response = requests.post(
            XLSX_DATA_REPORTING_LAMBDA,
            json=filepath,
        )
        json_response = response.json()
        data = json_response.get('data')

        start_date = data["Start date (yyyy-mm-dd)"]
        end_date = data["End date (yyyy-mm-dd)"]
        gross_tonnage = data["Gross tonnage"]
        deadweight_tonnage = data["DWT"]
        total_hours = data["Hours underway (h)"]
        total_distance = data["Distance Travelled (n.m)"]
        fuel_oil_burned = _process_fuel_types_for_xlsx(
            data["Fuel oil consumption (ton)"])
    # TODO: Error Handling

    extracted_data = StandardizedDataReportingData.objects.create(
        reporting_file=data_report,
        ship=data_report.ship,
        year=data_report.year,
        start_date=start_date,
        end_date=end_date,
        gross_tonnage=gross_tonnage,
        deadweight_tonnage=deadweight_tonnage,
        total_hours=total_hours,
        total_distance=total_distance,
        fuel_oil_burned=fuel_oil_burned,
    )

    return extracted_data


def _process_fuel_types_for_pdf(
    consumption_dict: dict[str, float]
) -> dict[str, float]:
    PDF_DATA_REPORTING_FUEL_MAP = {
        "Diesel/Gas Oil(Cf: 3.206)": CIIFuelType.MDGO,
        "LPG (Butane)(Cf: 3.030)": CIIFuelType.LPG_BUTANE,
        "LPG (Propane)(Cf: 3.000 )": CIIFuelType.LPG_PROPANE,
        "LNG (Cf: 2.750)": CIIFuelType.LNG,
        "LFO (Cf: 3.151)": CIIFuelType.LSFO,
        "HFO (Cf: 3.114)": CIIFuelType.HFO,
        "Methanol (Cf: 1.375)": CIIFuelType.METHANOL,
        "Ethanol (Cf: 1.913)": CIIFuelType.ETHANOL,
    }

    other = consumption_dict.pop("Other (……….)")
    other_cf = consumption_dict.pop("(Cf ;…..)")
    clean_dict = {}
    # TODO: Handle Other
    for key, value in consumption_dict.items():
        if value == 0:
            continue
        fuel_type = PDF_DATA_REPORTING_FUEL_MAP.get(key)
        clean_dict[fuel_type] = value
    return clean_dict


def _process_fuel_types_for_xlsx(
    consumption_dict: dict[str, float]
) -> dict[str, float]:
    XLSX_DATA_REPORTING_FUEL_MAP = {
        "Diesel/gas Oil (Cf:3.206)": CIIFuelType.MDGO,
        "LPG (Butane) (Cf:3.030)": CIIFuelType.LPG_BUTANE,
        "LPG (Propane) (Cf:3.000)": CIIFuelType.LPG_PROPANE,
        "LNG (Cf:2.750)": CIIFuelType.LNG,
        "LFO (Cf:3.151)": CIIFuelType.LSFO,
        "HFO (Cf:3.114)": CIIFuelType.HFO,
        "Methanol (Cf:1.375)": CIIFuelType.METHANOL,
        "Ethanol (Cf:1.913)": CIIFuelType.ETHANOL,
    }
    clean_dict = {}
    for key, value in consumption_dict.items():
        if value == 0:
            continue
        if "other" in key.lower():
            # TODO: Handle Other
            continue
        fuel_type = XLSX_DATA_REPORTING_FUEL_MAP.get(key)
        clean_dict[fuel_type] = value
    return clean_dict
