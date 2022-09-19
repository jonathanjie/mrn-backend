from decimal import Decimal
import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.gis.db import models

from auth0.models import User
from marinanet.enums import ReportTypes, ShipAccessPrivilege, ShipTypes, Status


### USERS ###

class Company(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=255)
    link = models.URLField()
    status = models.PositiveSmallIntegerField(choices=Status.choices)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "companies"


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
    imo_reg = models.PositiveIntegerField()
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

### REPORTS ###


class Voyage(models.model):
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


class ReportHeader(models.model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    voyage = models.ForeignKey(Voyage, on_delete=models.PROTECT)
    report_type = models.ChoiceField(choices=ReportTypes.choices)
    report_num = models.IntegerField()
    cargo_presence = models.BooleanField()
    timezone = models.IntegerField()
    datetime = models.DateTimeField()
    summer_time = models.BooleanField()
    position = models.PointField(srid=4326)
    # Note that for position, X is Longitude, Y is Lattitude
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
    distance_to_standby = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    hours_since_noon = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    hours_total = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    distance_obs_since_noon = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    distance_eng_since_noon = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    distance_eng_total = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    revolution_count = models.IntField(
        validators=[MinValueValidator(Decimal("0.0"))])
    speed_since_noon = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    rpm_since_noon = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    slip_since_noon = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    speed_avg = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    rpm_avg = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    slip_avg = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    weather = models.CharField(max_length=255)
    sea_state = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0)])
    wind_direction = models.DecimalField(
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("360"))
            ])
    wind_speed = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    heavy_weather_hours = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    heavy_weather_dist = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    heavy_weather_foc = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    heavy_weather_wind_direction = models.DecimalField(
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("360"))
            ])
    heavy_weather_wind_speed = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    heavy_weather_max_wave_ht = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    changed_speed = models.DecimalField()
    changed_foc = models.DecimalField()
    changed_rpm = models.DecimalField()
    changed_date = models.DecimalField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "noon_reports_at_sea"


class BunkerDetails(models.model):
    report_data = models.OneToOneField(ReportData, on_delete=models.PROTECT)
    consumed_lsfo = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    consumed_mgo = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    consumed_correction = models.CharField()
    consumed_remarks = models.CharField()
    received_lsfo = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    received_lsfo_time = models.DateTimeField()
    received_mgo = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    received_mgo_time = models.DateTimeField()
    received_meslo = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    received_meclo = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    received_geslo = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    received_freshwater = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    received_correction = models.CharField()
    received_remark = models.CharField()
    rob_lsfo = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    rob_mgo = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    rob_freshwater = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    rob_meslo = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    rob_mest = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    rob_meslo = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    rob_ meclo = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    rob_ geslo = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    evaporated_freshwater = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    consumed_freshwater = models.DecimalField(
        validators=[MinValueValidator(Decimal("0.0"))])
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "report_data_bunker_details"
