from django.db import models
from django.utils.translation import gettext_lazy as _


class Status(models.IntegerChoices):
    INACTIVE = 0, _("Inactive")
    ACTIVE = 1, _("Active")


class ShipAccessPrivilege(models.IntegerChoices):
    READ = 0, _("Read only access")
    WRITE = 1, _("Read and Write access")


class ShipType(models.TextChoices):
    CONTAINER = "CNTR", _("Container Ship")
    BULK_CARRIER = "BULK", _("Bulk Carrier")
    OIL_TANKER = "OIL", _("Oil Tanker")
    GAS_TANKER = "GAS", _("Gas/LNG Tanker")
    RORO = "RORO", _("Roll-On Roll-Off Ships")
    GENERAL_CARGO = "GEN", _("General Cargo Ship")
    REFRIGERATED_CARGO = "REFC", _("Refrigerated Cargo Carrier")
    COMBINATION_CARRIER = "COMB", _("Combination Carrier")
    LNG_CARRIER = "LNGC", _("LNG Carrier")
    RORO_VEHICLE_CARRIER = "RORV", _("Ro-Ro Cargo Ship (Vehicle Carrier)")
    RORO_PASSENGER_SHIP = "RORP", _("Ro-Ro Passenger Ship")
    CRUISE_PASSENGER_SHIP = "CRUZ", _("Cruise Passenger Ship")


class FuelType(models.TextChoices):
    HFO = "HFO", _("HFO")
    LSFO = "LSFO", _("LSFO")
    MDO = "MDO", _("MDO")
    MGO = "MGO", _("MGO")
    LPG_PROPANE = "LPGP", _("LPG (Propane)")
    LPG_BUTANE = "LPGB", _("LPG (Butane")
    METHANOL = "METH", _("Methanol")
    ETHANOL = "ETH", _("Ethanol")
    LNG = "LNG", _("LNG")


class CargoUnits(models.TextChoices):
    M3 = "M3", _("Cubic Meter")
    MT = "MT", _("Metric Ton")
    TEU = "TEU", _("TEU")
    CEU = "CEU", _("CEU")
