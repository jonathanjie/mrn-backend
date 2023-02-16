from decimal imprt Decimal

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
from carboncalc.models import CIIConfig
from core.models import Ship, ShipSpecs


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
