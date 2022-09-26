from django.db import models
from django.utils.translation import gettext_lazy as _


class Status(models.IntegerChoices):
    INACTIVE = 0, _("Inactive")
    ACTIVE = 1, _("Active")


class ShipAccessPrivilege(models.IntegerChoices):
    READ = 0, _("Read only access")
    WRITE = 1, _("Read and Write access")


class ShipTypes(models.TextChoices):
    CONTAINER = "CNTR", _("Container Ship")
    BULK_CARRIER = "BULK", _("Bulk Carrier")
    OIL_TANKER = "OIL", _("Oil Tanker")
    GAS_TANKER = "GAS", _("Gas/LNG Tanker")
    RORO = "RORO", _("Roll-On Roll-Off Ships")


class ReportTypes(models.TextChoices):
    NOON = "NOON", _("Noon at Sea")
    WAITING = "WAIT", _("Noon Waiting")
    IN_PORT = "PORT", _("Noon in Port")
    DEPARTURE = "DEP", _("Departure")
    ARRIVAL = "ARR", _("Arrival")
    BDN = "BDN", _("Bunker Delivery Note")


class CargoPresence(models.TextChoices):
    BALLAST = "BALL", _("Ballast")
    LADEN = "LADN", _("Laden")
    EASTBOUND = "EAST", _("Eastbound")
    WESTBOUND = "WEST", _("Westbound")


class Weather(models.TextChoices):
    BLUE_SKY = "B", _("Blue sky (Cloud 0-2)")
    FINE_CLOUDY = "BC", _("Fine but Cloudy (Cloud 3-7)")
    CLOUDY = "C", _("Cloudy (Cloud 8-10)")
    DRIZZLING = "D", _("Drizzling rain")
    FOG = "F", _("Fog")
    GLOOM = "G", _("Gloom")
    HAIL = "H", _("Hail")
    LIGHTNING = "L", _("Lightning")
    MIST = "M", _("Mist")
    OVERCAST = "O", _("Overcast (Cloud 10)")
    PASSING_SHOWERS = "P", _("Passing showers")
    SQUALLS = "Q", _("Squalls")
    RAIN = "R", _("Rain")
    SNOW = "S", _("Snow")
    THUNDER = "T", _("Thunder")
    UGLY = "U", _("Ugly threatening weather")
    DEW = "W", _("Dew")
    HAZE = "Z", _("Haze")


class Beaufort(models.IntegerChoices):
    CALM = 0, _("Calm")
    LIGHT_AIR = 1, _("Light air")
    LIGHT_BREEZE = 2, _("Light breeze")
    GENTLE_BREEZE = 3, _("Gentle breeze")
    MODERATE_BREEZE = 4, ("Moderate breeze")
    FRESH_BREEZE = 5, _("Fresh breeze")
    STRONG_BREEZE = 6, _("Strong breeze")
    NEAR_GALE = 7, _("Near gale")
    GALE = 8, _("Gale")
    STRONG_GALE = 9, _("Strong gale")
    STORM = 10, _("Storm")
    VIOLENT_STORM = 11, _("Violent storm")
    HURRICANE = 12, _("Hurricane")


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
