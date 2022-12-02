from decimal import Decimal
import uuid

from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation
)
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.gis.db import models
from django.db import models as dmodels
from django.forms import ModelForm
from timezone_field import TimeZoneField

from auth0.models import User
from marinanet.enums import (
    BeaufortScale,
    Cardinal_8,
    Cardinal_16,
    CargoPresence,
    ConsumptionType,
    DouglasScale,
    FuelType,
    GlacierIceCondition,
    ReportTypes,
    ShipAccessPrivilege,
    ShipTypes,
    Status,
    SwellScale,
    Weather,
)


class BaseModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


""" USER MODELS
"""


class Company(BaseModel):
    name = models.CharField(max_length=255)
    link = models.URLField()
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = "companies"
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class UserProfile(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.PROTECT, primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    role = models.CharField(max_length=255)
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = "profiles"


class Ship(BaseModel):
    name = models.CharField(max_length=255)
    imo_reg = models.PositiveIntegerField()     # 7 digits
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    ship_type = models.CharField(max_length=4, choices=ShipTypes.choices)
    assigned_users = models.ManyToManyField(
        User,
        through='ShipUser',
        through_fields=('ship', 'user')
    )
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = "ships"

    def __str__(self):
        return self.name


class ShipUser(BaseModel):
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    privilege = models.PositiveSmallIntegerField(
        choices=ShipAccessPrivilege.choices)
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = "ship_users"


""" REPORT MODELS
"""


class Voyage(BaseModel):
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    voyage_num = models.PositiveIntegerField()
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = "voyages"


class ReportHeader(BaseModel):
    voyage = models.ForeignKey(Voyage, on_delete=models.PROTECT)
    leg_num = models.PositiveSmallIntegerField()
    report_type = models.CharField(max_length=4, choices=ReportTypes.choices)
    report_num = models.PositiveIntegerField()
    report_date = models.DateTimeField()
    report_tz = TimeZoneField(use_pytz=False)
    summer_time = models.BooleanField()
    position = models.PointField(srid=4326)
    # Note that for position, X is Longitude, Y is Latitude
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = "report_headers"


class ReportData(BaseModel):
    report_header = models.OneToOneField(
        ReportHeader, on_delete=models.PROTECT, primary_key=True)

    class Meta:
        abstract = True


class Route(ReportData):
    departure_port = models.CharField(max_length=6)  # TODO: LOCODE
    departure_date = models.DateTimeField()
    arrival_port = models.CharField(max_length=6)  # TODO: LOCODE
    arrival_date = models.DateTimeField()


class WeatherData(ReportData):
    weather_notation = models.CharField(max_length=2, choices=Weather.choices)
    visibility = models.PositiveSmallIntegerField()
    wind_direction = models.CharField(
        max_length=3, choices=Cardinal_16.choices)
    wind_speed = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    sea_direction = models.CharField(
        max_length=2, choices=Cardinal_8.choices)
    sea_state = models.PositiveSmallIntegerField(choices=DouglasScale.choices)
    swell_direction = models.CharField(
        max_length=2, choices=Cardinal_8.choices)
    swell_scale = models.PositiveSmallIntegerField(choices=SwellScale.choices)
    air_pressure = models.PositiveSmallIntegerField()
    air_temperature_dry = models.DecimalField(max_digits=3, decimal_places=1)
    air_temperature_wet = models.DecimalField(max_digits=3, decimal_places=1)
    sea_temperature = models.DecimalField(max_digits=3, decimal_places=1)
    ice_condiction = models.CharField(
        max_length=4,
        choices=GlacierIceCondition.choices,
        default=GlacierIceCondition.NONE)
    # wind_direction = models.DecimalField(
    #     max_digits=4,
    #     decimal_places=1,
    #     validators=[
    #         MinValueValidator(Decimal("0.0")),
    #         MaxValueValidator(Decimal("360"))])
    # beaufort = models.PositiveSmallIntegerField(choices=BeaufortScale.choices)

    class Meta:
        db_table = "weather_data"


class HeavyWeatherData(ReportData):
    total_hours = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    observed_distance = models.DecimalField(
        max_digits=3,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))])
    fuel_consumption = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    wind_direction = models.CharField(
        max_length=3, choices=Cardinal_16.choices)
    wind_speed = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    sea_direction = models.CharField(
        max_length=2, choices=Cardinal_8.choices)
    sea_state = models.PositiveSmallIntegerField(choices=DouglasScale.choices)
    max_wave_height = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal("0.0"))])
    remarks = models.TextField()

    class Meta:
        db_table = "heavy_weather_data"


class DistancePerformanceData(ReportData):
    hours_since_noon = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("48"))])
    hours_total = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    distance_to_go = models.DecimalField(
        max_digits=5,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))])
    remarks_for_changes = models.TextField()
    distance_obs_since_noon = models.DecimalField(
        max_digits=3,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))])
    distance_obs_total = models.DecimalField(
        max_digits=5,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))])
    distance_eng_since_noon = models.DecimalField(
        max_digits=3,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))])
    distance_eng_total = models.DecimalField(
        max_digits=5,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))])
    revolution_count = models.IntegerField(
        validators=[MinValueValidator(0)])
    speed_since_noon = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    rpm_since_noon = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    slip_since_noon = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    speed_avg = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    rpm_avg = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    slip_avg = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])

    class Meta:
        db_table = "distance_performance_data"


class ConsumptionConditionData(ReportData):
    consumption_type = models.CharField(
        max_length=4, choices=ConsumptionType.choices)

    class Meta:
        db_table = "consumption_conduiion_data"
        unique_together = ["report_header", "consumption_type"]


# class ConsumptionDataCorrection(models.Model):
#     limit = models.Q(app_label="marinanet", model="fueloildata") | \
#         models.Q(app_label="marinanet", model="lubricatingoildata")
#     content_type = models.ForeignKey(
#         ContentType, limit_choices_to=limit, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey("content_type", "object_id")
#     correction = models.DecimalField(max_digits=7, decimal_places=2)
#     remarks = models.TextField()

#     class Meta:
#         indexes = [
#             models.Index(fields=["content_type", "object_id"]),
#         ]
#         db_table = "consumption_data_corrections"


class ConsumptionData(BaseModel):
    ccdata = models.ForeignKey(
        ConsumptionConditionData, on_delete=models.PROTECT)
    # correction = GenericRelation(ConsumptionDataCorrection)

    class Meta:
        abstract = True


class FuelOilData(ConsumptionData):
    fuel_oil_type = models.CharField(max_length=4, choices=FuelType.choices)
    total_consumption = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    receipt = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    debunkering = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    rob = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    breakdown = models.JSONField()

    class Meta:
        db_table = "fuel_oil_data"


class LubricatingOilData(ConsumptionData):
    fuel_oil_type = models.CharField(max_length=64)
    total_consumption = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    receipt = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    debunkering = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    rob = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])

    class Meta:
        db_table = "lubricating_oil_data"


class FreshWaterData(ConsumptionData):
    consumed = models.PositiveIntegerField()
    evaporated = models.PositiveIntegerField()
    received = models.PositiveIntegerField()
    discharged = models.PositiveIntegerField()
    rob = models.PositiveIntegerField()

    class Meta:
        db_table = "fresh_water_data"


class StoppageData(ReportData):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    duration = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    reduced_rpm = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    position = models.PointField(srid=4326)
    reason = models.CharField(max_length=4)
    remarks = models.TextField()

    class Meta:
        db_table = "stoppage_data"
