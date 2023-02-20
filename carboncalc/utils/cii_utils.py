from decimal import Decimal

from carboncalc.enums import ApplicableCII, CIIShipType
from core.enums import ShipType
from core.models import Ship


CII_SHIP_TYPE_MAP = {
    ShipType.CONTAINER: CIIShipType.CONTAINER,
    ShipType.OIL_TANKER: CIIShipType.OIL_TANKER,
    ShipType.RORO: CIIShipType.RORO,
    ShipType.REFRIGERATED_CARGO: CIIShipType.REFRIGERATED_CARGO,
    ShipType.COMBINATION_CARRIER: CIIShipType.COMBINATION_CARRIER,
    ShipType.RORO_VEHICLE_CARRIER: CIIShipType.RORO_VEHICLE_CARRIER,
    ShipType.RORO_PASSENGER_SHIP: CIIShipType.RORO_PASSENGER_SHIP,
    ShipType.CRUISE_PASSENGER_SHIP: CIIShipType.CRUISE_PASSENGER_SHIP,
}

def get_cii_ship_type(
    ship: Ship
) -> str:
    ship_type = ship.ship_type
    cii_ship_type = CII_SHIP_TYPE_MAP.get(ship_type, None)
    if not cii_ship_type:
        dwt = ship.shipspecs.deadweight_tonnage

        if ship_type == ShipType.BULK_CARRIER:
            if dwt >= 279000:
                cii_ship_type = CIIShipType.BULK_CARRIER_GTE_27900
            else:
                cii_ship_type = CIIShipType.BULK_CARRIER_LT_279000

        elif ship_type == ShipType.GAS_TANKER:
            if dwt >= 65000:
                cii_ship_type = CIIShipType.GAS_TANKER_GTE_65000
            else:
                cii_ship_type = CIIShipType.GAS_TANKER_LT_65000

        elif ship_type == ShipType.GENERAL_CARGO:
            if dwt >= 20000:
                cii_ship_type = CIIShipType.GENERAL_CARGO_GTE_20000
            else:
                cii_ship_type = CIIShipType.GENERAL_CARGO_LT_20000

        elif ship_type == ShipType.LNG_CARRIER:
            if dwt >= 100000:
                cii_ship_type = CIIShipType.LNG_CARRIER_GTE_100000
            elif dwt > 65000:
                cii_ship_type = CIIShipType.LNG_CARRIER_GTE_65000
            else:
                cii_ship_type = CIIShipType.LNG_CARRIER_LT_65000

    return cii_ship_type


AER_TYPES = (
    ShipType.BULK_CARRIER,
    ShipType.COMBINATION_CARRIER,
    ShipType.CONTAINER,
    ShipType.GAS_TANKER,
    ShipType.GENERAL_CARGO,
    ShipType.LNG_CARRIER,
    ShipType.OIL_TANKER,
    ShipType.REFRIGERATED_CARGO,
    ShipType.RORO,
)

CGDIST_TYPES = (
    ShipType.CRUISE_PASSENGER_SHIP,
    ShipType.RORO_PASSENGER_SHIP,
    ShipType.RORO_VEHICLE_CARRIER,
)

def get_applicable_cii(
    ship: Ship
):
    ship_type = ship.ship_type
    if ship_type in AER_TYPES:
        return ApplicableCII.AER
    else:
        return ApplicableCII.CGDIST


def get_ship_capacity_value(
    ship: Ship
) -> Decimal:
    applicable_cii = ship.ciiconfig.applicable_cii
    if applicable_cii == ApplicableCII.AER:
        return ship.shipspecs.deadweight_tonnage
    elif applicable_cii == ApplicableCII.CGDIST:
        return ship.shipspecs.gross_tonnage
