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
    GENERAL_CARGO = "GEN", _("General Cargo Ship")
    REFRIGERATED_CARGO = "REFC", _("Refrigerated Cargo Carrier")
    COMBINATION_CARRIER = "COMB", _("Combination Carrier")
    LNG_CARRIER = "LNGC", _("LNG Carrier")
    RORO_VEHICLE_CARRIER = "RORV", _("Ro-Ro Cargo Ship (Vehicle Carrier)")
    RORO_PASSENGER_SHIP = "RORP", _("Ro-Ro Passenger Ship")
    CRUISE_PASSENGER_SHIP = "CRUZ", _("Cruise Passenger Ship")


class ReportTypes(models.TextChoices):
    NOON = "NOON", _("Noon at Sea")
    DEP_SBY = "DSBY", _("Departure: Standby")
    DEP_COSP = "DCSP", _("Departure: COSP")
    ARR_SBY = "ASBY", _("Arrival: Standby")
    ARR_FWE = "AFWE", _("Arrival: FWE")
    BDN = "BDN", _("Bunker Delivery Note")
    EVENT = "EVNT", _("Event in Harbour")


class CargoPresence(models.TextChoices):
    BALLAST = "BALL", _("Ballast")
    LADEN = "LADN", _("Laden")
    EASTBOUND = "EAST", _("Eastbound")
    WESTBOUND = "WEST", _("Westbound")


class Cardinal_4(models.TextChoices):
    NORTH = "N", _("North")
    EAST = "E", _("East")
    SOUTH = "S", _("South")
    WEST = "W", _("West")


class Cardinal_8(models.TextChoices):
    NORTH = "N", _("North")
    EAST = "E", _("East")
    SOUTH = "S", _("South")
    WEST = "W", _("West")
    NORTHEAST = "NE", _("Northeast")
    SOUTHEAST = "SE", _("Southeast")
    SOUTHWEST = "SW", _("Southwest")
    NORTHWEST = "NW", _("Northwest")


class Cardinal_16(models.TextChoices):
    NORTH = "N", _("North")
    EAST = "E", _("East")
    SOUTH = "S", _("South")
    WEST = "W", _("West")
    NORTHEAST = "NE", _("Northeast")
    SOUTHEAST = "SE", _("Southeast")
    SOUTHWEST = "SW", _("Southwest")
    NORTHWEST = "NW", _("Northwest")
    NORTH_NORTHEAST = "NNE", _("North-Northeast")
    EAST_NORTHEAST = "ENE", _("East-Northeast")
    EAST_SOUTHEAST = "ESE", _("East-Southeast")
    SOUTH_SOUTHEAST = "SSE", _("South-Southeast")
    SOUTH_SOUTHWEST = "SSW", _("South-Southwest")
    WEST_SOUTHWEST = "WSW", _("West-Southwest")
    WEST_NORTHWEST = "WNW", _("West-Northwest")
    NORTH_NORTHWEST = "NNW", _("North-Northwest")


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


class BeaufortScale(models.IntegerChoices):
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


class DouglasScale(models.IntegerChoices):
    CALM_GLASSY = 0, ("Calm (Glassy)")
    CALM_RIPPLED = 1, ("Calm (Rippled)")
    SMOOTH_WAVELETS = 2, ("Smooth (Wavelets)")
    SLIGHT = 3, ("Slight")
    MODERATE = 4, ("Moderate")
    ROUGH = 5, ("Rough")
    VERY_ROUGH = 6, ("Very Rough")
    HIGH = 7, ("High")
    VERY_HIGH = 8, ("Very High")
    PHENOMENAL = 9, ("Phenomal")


class SwellScale(models.IntegerChoices):
    NO_SWELL = 0, ("No Swell")
    LOW_SWELL_SHORT_AVE = 1, ("Low Swell (Short or Average)")
    LOW_SWELL_LONG = 2, ("Low Swell (Long)")
    MODERATE_SHORT = 3, ("Moderate Swell (Short)")
    MODERATE_AVERAGE = 4, ("Moderate Swell (Average)")
    MODERATE_LONG = 5, ("Moderate Swell (Long)")
    HEAVY_SWELL_SHORT = 6, ("Heavy Swell (Short)")
    HEAVY_SWELL_AVERAGE = 7, ("Heavy Swell (Moderate)")
    HEAVY_SWELL_LONG = 8, ("Heavy Swell (Long)")
    CONFUSED_SWELL = 9, ("Confused Swell")


class ConsumptionType(models.TextChoices):
    NOON_TO_NOON = "NTON", _("Noon to Noon")
    LAST_TO_SBY = "LTOS", _("Last Report to Standby")
    IN_HARBOUR_PORT = "INHP", _("In Harbour / In Port")
    STANDBY_TO_RUNUP = "STOR", _("Standby to Run Up")
    NOON_TO_STANDBY = "NTOS", _("Noon to Standby")
    STANDBY_TO_FWE = "STOF", _("Standby to FWE")
    LAST_TO_EVENT = "LTOE", _("Last Report to Event")


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


class GlacierIceCondition(models.TextChoices):
    NONE = "NONE", _("NONE")
    LOW = "LOW", _("LOW")
    MODERATE = "MOD", _("MODERATE")
    HIGH = "HIGH", _("HIGH")
    EXTENSIVE = "EXT", _("EXTENSIVE")
