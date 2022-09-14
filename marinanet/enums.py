from django.db import models


class Status(models.IntegerChoices):
    INACTIVE = 0, _("Inactive")
    ACTIVE = 1, _("Active")


class ShipAccessPrivilege(models.IntegerChoices):
    READ = 0, _("Read only access")
    WRITE = 1, _("Read and Write access")
