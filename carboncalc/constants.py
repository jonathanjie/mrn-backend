from carboncalc.enums import CIIFuelType, CIIShipType

CONVERSION_FACTORS = {
    CIIFuelType.MDGO: '3.206',
    CIIFuelType.LSFO: '3.151',
    CIIFuelType.HFO: '3.114',
    CIIFuelType.LPG_PROPANE: '3.000',
    CIIFuelType.LPG_BUTANE: '3.030',
    CIIFuelType.LNG: '2.750',
    CIIFuelType.METHANOL: '1.375',
    CIIFuelType.ETHANOL: '1.913',
}


REFERENCE_LINE_CONSTANTS = {
    # Ship Type: (a, c) #TBIYTB :D
    CIIShipType.BULK_CARRIER_GTE_279000: ('4745', '0.622'),
    CIIShipType.BULK_CARRIER_LT_279000: ('4745', '0.622'),
    CIIShipType.GAS_TANKER_GTE_65000: ('144050000000', '2.071'),
    CIIShipType.GAS_TANKER_LT_65000: ('8104', '0.639'),
    CIIShipType.OIL_TANKER: ('5247', '0.610'),
    CIIShipType.CONTAINER: ('1984', '0.489'),
    CIIShipType.GENERAL_CARGO_GTE_20000: ('31948', '0.792'),
    CIIShipType.GENERAL_CARGO_LT_20000: ('588', '0.3885'),
    CIIShipType.REFRIGERATED_CARGO: ('4600', '0.557'),
    CIIShipType.COMBINATION_CARRIER: ('40853', '0.812'),
    CIIShipType.LNG_CARRIER_GTE_100000: ('9.827', '0'),
    CIIShipType.LNG_CARRIER_GTE_65000: ('144790000000000', '2.673'),
    CIIShipType.LNG_CARRIER_LT_65000: ('144790000000000', '2.673'),
    CIIShipType.RORO: ('10952', '0.637'),
    CIIShipType.RORO_VEHICLE_CARRIER: ('5739', '0.631'),
    CIIShipType.RORO_PASSENGER_SHIP: ('7540', '0.587'),
    CIIShipType.CRUISE_PASSENGER_SHIP: ('930', '0.383'),
}


REDUCTION_FACTORS = {
    2019: '0.00',
    2020: '0.01',
    2021: '0.02',
    2022: '0.03',
    2023: '0.05',
    2024: '0.07',
    2025: '0.09',
    2026: '0.11',
}


DD_VECTORS = {
    # Ship Type: (d1, d2, d3, d4)
    CIIShipType.BULK_CARRIER_GTE_279000: ('0.86', '0.94', '1.06', '1.18'),
    CIIShipType.BULK_CARRIER_LT_279000: ('0.86', '0.94', '1.06', '1.18'),
    CIIShipType.GAS_TANKER_GTE_65000: ('0.81', '0.91', '1.12', '1.44'),
    CIIShipType.GAS_TANKER_LT_65000: ('0.85', '0.95', '1.06', '1.25'),
    CIIShipType.OIL_TANKER: ('0.82', '0.93', '1.08', '1.28'),
    CIIShipType.CONTAINER: ('0.83', '0.94', '1.07', '1.19'),
    CIIShipType.GENERAL_CARGO_GTE_20000: ('0.83', '0.94', '1.06', '1.19'),
    CIIShipType.GENERAL_CARGO_LT_20000: ('0.83', '0.94', '1.06', '1.19'),
    CIIShipType.REFRIGERATED_CARGO: ('0.78', '0.91', '1.07', '1.20'),
    CIIShipType.COMBINATION_CARRIER: ('0.87', '0.96', '1.06', '1.14'),
    CIIShipType.LNG_CARRIER_GTE_100000: ('0.89', '0.98', '1.06', '1.13'),
    CIIShipType.LNG_CARRIER_GTE_65000: ('0.78', '0.92', '1.10', '1.37'),
    CIIShipType.LNG_CARRIER_LT_65000: ('0.78', '0.92', '1.10', '1.37'),
    CIIShipType.RORO: ('0.66', '0.90', '1.11', '1.37'),
    CIIShipType.RORO_VEHICLE_CARRIER: ('0.86', '0.94', '1.06', '1.16'),
    CIIShipType.RORO_PASSENGER_SHIP: ('0.72', '0.90', '1.12', '1.41'),
    CIIShipType.CRUISE_PASSENGER_SHIP: ('0.87', '0.95', '1.06', '1.16'),
}


CONVERSION_FACTOR_REGEX = "\(Cf: ?[0-9]*\.[0-9]+\)$"
