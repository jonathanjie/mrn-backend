from decimal import Decimal
import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.gis.db import models
from django.forms import ModelForm

from auth0.models import User
from marinanet.enums import (
    Beaufort,
    CargoPresence,
    FuelType,
    ReportTypes,
    ShipAccessPrivilege,
    ShipTypes,
    Status,
    Weather,
)


""" USER MODELS
"""


class Company(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=255)
    link = models.URLField()
    status = models.PositiveSmallIntegerField(choices=Status.choices)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "companies"
        verbose_name_plural = "companies"


class Profile(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.OneToOneField(
        User, on_delete=models.PROTECT, primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    role = models.CharField(max_length=255)
    status = models.PositiveSmallIntegerField(choices=Status.choices)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "profiles"


class Ship(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=255)
    imo_reg = models.PositiveIntegerField()     # 7 digits
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    ship_type = models.CharField(max_length=4, choices=ShipTypes.choices)
    assigned_users = models.ManyToManyField(
        User,
        through='ShipUser',
        through_fields=('ship', 'user')
    )
    status = models.PositiveSmallIntegerField(choices=Status.choices)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ships"


class ShipUser(models.Model):
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    privilege = models.PositiveSmallIntegerField(
        choices=ShipAccessPrivilege.choices)
    status = models.PositiveSmallIntegerField(choices=Status.choices)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ship_users"


""" REPORT MODELS
"""


class Voyage(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    voyage_num = models.PositiveIntegerField()
    departure_date = models.DateTimeField()
    departure_port = models.CharField(max_length=6)
    arrival_date = models.DateTimeField()
    arrival_port = models.CharField(max_length=6)
    status = models.PositiveSmallIntegerField(choices=Status.choices)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "voyages"


class ReportHeader(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    voyage = models.ForeignKey(Voyage, on_delete=models.PROTECT)
    report_type = models.CharField(max_length=4, choices=ReportTypes.choices)
    report_num = models.IntegerField()
    cargo_presence = models.TextField(
        max_length=4, choices=CargoPresence.choices)
    summer_time = models.BooleanField()
    position = models.PointField(srid=4326)
    # Note that for position, X is Longitude, Y is Latitude
    status = models.PositiveSmallIntegerField(choices=Status.choices)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "report_headers"


class ReportData(models.Model):
    report_header = models.OneToOneField(
        ReportHeader, on_delete=models.PROTECT, primary_key=True)

    class Meta:
        abstract = True


class NoonReportAtSea(ReportData):
    distance_to_go = models.DecimalField(
        max_digits=5,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))])
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
    distance_obs_since_noon = models.DecimalField(
        max_digits=3,
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
    # changed_speed = models.DecimalField()
    # changed_foc = models.DecimalField()
    # changed_rpm = models.DecimalField()
    # changed_date = models.DecimalField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "noon_reports_at_sea"


class WeatherData(models.Model):
    report_data = models.OneToOneField(
        ReportHeader, on_delete=models.PROTECT, primary_key=True)
    weather = models.TextField(max_length=2, choices=Weather.choices)
    sea_state = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(9)])
    wind_direction = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("360"))])
    wind_speed = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal("0.0"))])
    beaufort = models.PositiveSmallIntegerField(choices=Beaufort.choices)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "weather_data"


class HeavyWeatherData(models.Model):
    report_data = models.OneToOneField(
        ReportHeader, on_delete=models.PROTECT, primary_key=True)
    heavy_weather_hours = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    heavy_weather_dist = models.DecimalField(
        max_digits=3,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))])
    heavy_weather_consumption = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    heavy_weather_wind_direction = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("360"))])
    heavy_weather_wind_speed = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal("0.0"))])
    heavy_weather_max_wave_ht = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal("0.0"))])
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "heavy_weather_data"


class BunkerData(models.Model):
    report_data = models.ForeignKey(
        ReportHeader, on_delete=models.PROTECT)
    fuel_type = models.TextField(max_length=4, choices=FuelType.choices)
    rob = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    me_consumed = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    aux_consumed = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    boiler_consumed = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    gas_generator_consumed = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    total_consumed = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    correction = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    remarks = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bunker_data"
        unique_together = ["report_data", "fuel_type"]


class FreshWaterData(models.Model):
    report_data = models.OneToOneField(
        ReportHeader, on_delete=models.PROTECT, primary_key=True)
    rob = models.PositiveIntegerField()
    consumed = models.PositiveIntegerField()
    evaporated = models.PositiveIntegerField()
    correction = models.IntegerField()
    remarks = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fresh_water_data"
