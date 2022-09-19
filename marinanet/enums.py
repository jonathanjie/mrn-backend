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
    NOON = "NOON", _("Noon")
    DEPARTURE = "DEP", _("Departure")
    ARRIVAL = "ARR", _("Arrival")
    BDN = "BDN", _("Bunker Delivery Note")


class NoonReportTypes(models.TextChoices):
    NOON_SEA = "SEA", _("Noon at Sea")
    NOON_WAITING = "WAIT", _("Noon Waiting")
    NOON_IN_PORT = "PORT", _("Noon in Port")
