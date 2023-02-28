from django.db import models
from django.utils.translation import gettext_lazy as _


class DCSType(models.IntegerChoices):
    TYPE_1 = 1, _("DCS Type 1")
    TYPE_2 = 2, _("DCS Type 2")
