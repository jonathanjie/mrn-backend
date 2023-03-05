from decimal import Decimal

from carboncalc.constants import (
    CONVERSION_FACTORS,
    DD_VECTORS,
    REDUCTION_FACTORS,
    REFERENCE_LINE_CONSTANTS,
)
from carboncalc.enums import (
    ApplicableCII,
    CIIGrade,
    DCSMethod,
)
from carboncalc.models import (
    CalculatedCII,
    CIIConfig,
    CIIRawData,
    CIIShipYearBoundaries,
)
from carboncalc.utils import cii_utils
from core.models import Ship


def calculate_cii_reference_line(
    cii_ship_type: str,
    capacity: Decimal,
) -> Decimal:
    a, c = REFERENCE_LINE_CONSTANTS.get(cii_ship_type)
    a, c = Decimal(a), Decimal(c)
    return a * ((capacity)**(-c))


def calculate_required_cii(
    cii_reference_line: Decimal,
    year: int,
) -> Decimal:
    reduction_factor = REDUCTION_FACTORS.get(year)
    reduction_factor = Decimal(reduction_factor)
    # TODO: Handle year out of range
    return (1 - reduction_factor) * cii_reference_line


def calculate_cii_rating_boundaries(
    cii_ship_type: str,
    required_cii: Decimal,
    year: int
) -> dict[str, Decimal]:
    d1, d2, d3, d4 = DD_VECTORS.get(cii_ship_type)
    d1, d2, d3, d4 = Decimal(d1), Decimal(d2), Decimal(d3), Decimal(d4)

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
        cii_ship_type=cii_ship_type,
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


def populate_boundaries_for_ship(
    ship: Ship,
) -> None:
    for year in REDUCTION_FACTORS.keys():
        calculate_cii_ship_year_boundaries_for_ship(
            ship=ship,
            year=year,
        )


def calculate_co2_from_fuel_burn(
    fuel_burn_dict: dict[str, str],
) -> Decimal:
    total_co2 = Decimal(0)
    for fuel, burn in fuel_burn_dict.items():
        cf = CONVERSION_FACTORS.get(fuel)
        co2_for_fuel = Decimal(cf) * Decimal(burn) * Decimal(1000000)
        total_co2 += co2_for_fuel
    return total_co2


def calculate_cii_for_ship(
    co2_emissions: Decimal,
    tonnage: Decimal,
    distance_travelled: Decimal,
) -> Decimal:
    return co2_emissions / (tonnage * distance_travelled)


def determine_cii_grade_for_ship(
    ship: Ship,
    year: int,
    cii_value: Decimal,
):
    cii_boundaries = CIIShipYearBoundaries.objects.get(ship=ship, year=year)
    if cii_value <= cii_boundaries.boundary_a:
        grade = CIIGrade.A
    elif cii_value <= cii_boundaries.boundary_b:
        grade = CIIGrade.B
    elif cii_value <= cii_boundaries.boundary_c:
        grade = CIIGrade.C
    elif cii_value <= cii_boundaries.boundary_d:
        grade = CIIGrade.D
    else:
        grade = CIIGrade.E
    return grade


def process_cii_raw_data(
    cii_raw_data: CIIRawData,
):
    ship = cii_raw_data.ship
    config = ship.ciiconfig
    if config.applicable_cii == ApplicableCII.AER:
        tonnage = ship.shipspecs.deadweight_tonnage
    else:
        tonnage = ship.shipspecs.gross_tonnage
    total_co2_emissions = calculate_co2_from_fuel_burn(
        cii_raw_data.fuel_oil_burned)
    cii = calculate_cii_for_ship(
        co2_emissions=total_co2_emissions,
        tonnage=tonnage,
        distance_travelled=cii_raw_data.distance_sailed)
    grade = determine_cii_grade_for_ship(
        ship=cii_raw_data.ship,
        year=cii_raw_data.year,
        cii_value=cii)
    calculated_cii, _ = CalculatedCII.objects.update_or_create(
        ship=cii_raw_data.ship,
        year=cii_raw_data.year,
        defaults={
            'value': cii,
            'grade': grade,
        })
    return calculated_cii


def process_cii_calculator(
    ship: Ship,
    distance: Decimal,
    fuel_burn_dict: dict[str, str],
    target_cii_grade: str
):
    config = ship.ciiconfig
    if config.applicable_cii == ApplicableCII.AER:
        tonnage = ship.shipspecs.deadweight_tonnage
    else:
        tonnage = ship.shipspecs.gross_tonnage
    boundaries = CIIShipYearBoundaries.objects.get(ship=ship, year=2023)

    emissions = {}
    total_emission = Decimal(0)
    for fuel, consumption in fuel_burn_dict.items():
        cf = CONVERSION_FACTORS.get(fuel)
        emission_for_fuel = Decimal(cf) * Decimal(consumption) * Decimal(1000000)
        emissions[fuel] = emission_for_fuel
        total_emission += emission_for_fuel
    estimated_cii = calculate_cii_for_ship(
        co2_emissions=total_emission,
        tonnage=tonnage,
        distance_travelled=distance)
    estimated_cii_grade = determine_cii_grade_for_ship(
        ship=ship, year=2023, cii_value=estimated_cii)

    target_cii_boundary = boundaries.get_boundary_for_grade(target_cii_grade)
    target_emission_max = target_cii_boundary * (distance * tonnage)
    target_emission_budget = target_emission_max - total_emission
    target_fuel_projection = {}
    for fuel, consumption in fuel_burn_dict.items():
        cf = CONVERSION_FACTORS.get(fuel)
        budget_for_fuel = (emissions[fuel] / total_emission) * target_emission_budget
        target_fuel_projection[fuel] = budget_for_fuel / Decimal(1000000) / Decimal(cf)

    minimum_cii_grade = CIIGrade.C
    minimum_cii_boundary = boundaries.get_boundary_for_grade(minimum_cii_grade)
    minimum_emission_max = minimum_cii_boundary * (distance * tonnage)
    minimum_emission_budget = minimum_emission_max - total_emission
    minimum_fuel_projection = {}
    for fuel, consumption in fuel_burn_dict.items():
        cf = CONVERSION_FACTORS.get(fuel)
        budget_for_fuel = (emissions[fuel] / total_emission) * minimum_emission_budget
        minimum_fuel_projection[fuel] = budget_for_fuel / Decimal(1000000) / Decimal(cf)
    return_dict = {
        'estimated_cii_grade': estimated_cii_grade,
        'target_cii_grade': target_cii_grade,
        'target_cii_boundary': target_cii_boundary,
        'target_emission_budget': target_emission_budget / 1000,
        'target_fuel_projection': target_fuel_projection,
        'minimum_cii_grade': minimum_cii_grade,
        'minimum_cii_boundary': minimum_cii_boundary,
        'minimum_emission_budget': minimum_emission_budget / 1000,
        'minimum_fuel_projection': minimum_fuel_projection,
    }
    return return_dict



