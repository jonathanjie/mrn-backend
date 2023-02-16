from django.db import models
from django.utils.translation import gettext_lazy as _


class EnergyEfficiencyIndexType(models.TextChoices):
    EEXI = "EEXI", _("EEXI")
    EEDI = "EEDI", _("EEDI")


class CIIShipType(models.TextChoices):
    CONTAINER = "CNTR", _("Container Ship")
    BULK_CARRIER_GTE_279000 = "BULK_GTE_279000", _("Bulk Carrier (DWT >= 279000)")
    BULK_CARRIER_LT_279000 = "BULK_LT27900", _("Bulk Carrier (DWT < 279000)")
    OIL_TANKER = "OIL", _("Oil Tanker")
    GAS_TANKER_GTE_65000 = "GAS_GTE_65000", _("Gas/LNG Tanker (DWT >= 65000)")
    GAS_TANKER_LT_65000 = "GAS_LT_65000", _("Gas/LNG Tanker (DWT < 65000)")
    RORO = "RORO", _("Roll-On Roll-Off Ship")
    GENERAL_CARGO_GTE_20000 = "GEN_GTE_20000", _("General Cargo Ship (DWT >= 20000)")
    GENERAL_CARGO_LT_20000 = "GEN_LT_20000", _("General Cargo Ship (DWT < 20000)")
    REFRIGERATED_CARGO = "REFC", _("Refrigerated Cargo Carrier")
    COMBINATION_CARRIER = "COMB", _("Combination Carrier")
    LNG_CARRIER_GTE_100000 = "LNGC_GTE_100000", _("LNG Carrier (DWT >= 100000)")
    LNG_CARRIER_GTE_65000 = "LNGC_GTE_65000", _("LNG Carrier (100000 > DWT >= 65000)")
    LNG_CARRIER_LT_65000 = "LNGC_LT_65000", _("LNG Carrier (DWT < 65000)")
    RORO_VEHICLE_CARRIER = "RORV", _("Ro-Ro Cargo Ship (Vehicle Carrier)")
    RORO_PASSENGER_SHIP = "RORP", _("Ro-Ro Passenger Ship")
    CRUISE_PASSENGER_SHIP = "CRUZ", _("Cruise Passenger Ship")


class ApplicableCII(models.TextChoices):
    AER = "AER", _("AER")
    CGDIST = "CGDIST", _("cgDIST")


class TrialCII(models.TextChoices):
    EEPI = "EEPI", _("EEPI")
    CBDIST = "CBDIST", _("cbDIST")
    CLDIST = "CLDIST", _("clDIST")
    EEOI = "EEOI", _("EEOI")


class DCSMethod(models.TextChoices):
    METHOD_1 = "DCS1", _("DCS Method 1")
    METHOD_2 = "DCS2", _("DCS Method 2")
    METHOD_3 = "DCS3", _("DCS Method 3")


class MRVMethod(models.TextChoices):
    METHOD_A = "MRVA", _("MRV Method A")
    METHOD_B = "MRVB", _("MRV Method B")
    METHOD_C = "MRVC", _("MRV Method C")
    METHOD_D = "MRVD", _("MRV Method D")


class CIIGrade(models.TextChoices):
    A = "A", _("CII Grade A")
    B = "B", _("CII Grade A")
    C = "C", _("CII Grade A")
    D = "D", _("CII Grade A")
    E = "E", _("CII Grade A")
