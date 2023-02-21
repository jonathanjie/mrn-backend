from decimal import Decimal
import requests

from carboncalc.constants import (
    CONVERSION_FACTORS,
    DD_VECTORS,
    REDUCTION_FACTORS,
    REFERENCE_LINE_CONSTANTS,
)
from carboncalc.enums import (
    ApplicableCII,
    CIIFuelType,
    CIIGrade,
    DCSMethod,
)
from carboncalc.models import (
    CIIConfig,
    CIIShipYearBoundaries,
    StandardizedDataReportingData,
    StandardizedDataReportingFile,
)
from carboncalc.utils import cii_utils
from core.enums import FuelType
from core.models import Ship, ShipSpecs
from utils.filetype_utils import get_file_extension


def calculate_cii_reference_line(
    cii_ship_type: str,
    capacity: Decimal,
) -> Decimal:
    a, c = REFERENCE_LINE_CONSTANTS.get(cii_ship_type)

    return a * (capacity)**(c)


def calculate_required_cii(
    cii_reference_line,
    year,
) -> Decimal:
    reduction_factor = REDUCTION_FACTORS.get(year)
    # TODO: Handle year out of range
    return (1 - reduction_factor) * cii_reference_line


def calculate_cii_rating_boundaries(
    cii_ship_type: str,
    required_cii: Decimal,
    year: int
) -> dict[str, Decimal]:
    d1, d2, d3, d4 = DD_VECTORS.get(cii_ship_type)

    a_limit = d1 * required_cii
    b_limit = d2 * required_cii
    c_limit = d3 * required_cii
    d_limit = d4 * required_cii

    limits = {
        CIIGrade.A: a_limit,
        CIIGrade.B: b_limit,
        CIIGrade.C: c_limit,
        CIIGrade.D: d_limit
    }

    return limits


def calculate_cii_ship_year_boundaries_for_ship(
    ship: Ship,
    year: int
) -> CIIShipYearBoundaries:
    cii_ship_type = cii_utils.get_cii_ship_type(ship)
    capacity = cii_utils.get_ship_capacity_value(ship)

    ref_line = calculate_cii_reference_line(
        cii_ship_type=cii_ship_type,
        capacity=capacity,
    )
    required_cii = calculate_required_cii(
        cii_reference_line=ref_line,
        year=year,
    )
    cii_rating_boundaries = calculate_cii_rating_boundaries(
        cii_ship_type = cii_ship_type,
        required_cii=required_cii,
        year=year,
    )
    cii_ship_year_boundaries, _ = CIIShipYearBoundaries.objects.update_or_create(
        ship=ship,
        year=year,
        defaults={
            'boundary_a': cii_rating_boundaries[CIIGrade.A],
            'boundary_b': cii_rating_boundaries[CIIGrade.B],
            'boundary_c': cii_rating_boundaries[CIIGrade.C],
            'boundary_d': cii_rating_boundaries[CIIGrade.D],
        }

    )
    return cii_ship_year_boundaries


PDF_DATA_REPORTING_LAMBDA = "https://neapj5jo27o6a22mxs7lkb56ny0jiuzu.lambda-url.ap-southeast-1.on.aws/"
XLSX_DATA_REPORTING_LAMBDA = "https://ykmupploq5r6j5ws3jqb5g76yi0zcqwu.lambda-url.ap-southeast-1.on.aws/"

def process_standardized_data_reporting_file(
    data_report: StandardizedDataReportingFile,
):
    file_extension = get_file_extension(data_report.s3_file_path)
    filepath = {
        'filepath': 'testing/86360acf-d109-47da-87ef-3a7d7499619g/sample_kr_cii.pdf',
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
        fuel_oil_burned = _process_fuel_types_for_pdf(data["Fuel oil consumption(t)"])
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
        fuel_oil_burned = _process_fuel_types_for_xlsx(data["Fuel oil consumption (ton)"])
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

def _process_fuel_types_for_pdf(
    consumption_dict: dict[str, float]
) -> dict[str, float]:
    other = consumption_dict.pop("Other (……….)")
    other_cf = consumption_dict.pop("(Cf ;…..)")
    clean_dict = {}
    # TODO: Handle Other
    for key,value in consumption_dict:
        if value == 0:
            continue
        fuel_type = PDF_DATA_REPORTING_FUEL_MAP.get(key)
        clean_dict[fuel_type] = value
    return clean_dict

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

def _process_fuel_types_for_xlsx(
    consumption_dict: dict[str, float]
) -> dict[str, float]:
    clean_dict = {}
    for key,value in consumption_dict:
        if value == 0:
            continue
        if "other" in key.lower():
            # TODO: Handle Other
            continue
        fuel_type = XLSX_DATA_REPORTING_FUEL_MAP.get(key)
        clean_dict[fuel_type] = value
    return clean_dict
