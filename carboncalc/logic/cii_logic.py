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
    CIIConfig,
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
