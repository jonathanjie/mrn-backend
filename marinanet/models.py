import uuid

from django.db import models

from auth0.models import User
from marinanet.enums import ShipAccessPrivilege, ShipTypes, Status


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
    privilege = models.PositiveSmallIntegerField(choices=ShipAccessPrivilege.choices)
    status = models.PositiveSmallIntegerField(choices=Status.choices)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ship_users"

### REPORTS ###


# class Voyage(models.model):
#     uuid = models.UUIDField(default=uuid.uuid4, unique=True)
#     ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
#     voyage_num = models.IntegerField()
#     departure_date = models.DateTimeField()
#     departure_port = models.CharField(max_length=64)
#     arrival_date = models.DateTimeField()
#     arrival_port = models.CharField(max_length=64)
#     status = models.PositiveSmallIntegerField(choices=Status.choices)
#     date_created = models.DateTimeField(auto_now_add=True)
#     date_modified = models.DateTimeField(auto_now=True)


# class ReportHeader(models.model):
#     uuid = models.UUIDField(default=uuid.uuid4, unique=True)
#     voyage = models.ForeignKey(Voyage, on_delete=models.PROTECT)
#     report_type = models.ChoiceField(choices=ReportTypes.choices)
#     report_num = models.IntegerField()
#     cargo_presence = models.BooleanField()
#     timezone = models.IntegerField()
#     datetime = models.DateTimeField(auto_now_add=True)
#     summer_time = models.BooleanField()
#     # position = models.PointField() TODO
#     status = models.PositiveSmallIntegerField(choices=Status.choices)
#     date_created = models.DateTimeField(auto_now_add=True)
#     date_modified = models.DateTimeField(auto_now=True)


# class NoonReportHeader(models.model):
#     report_header = models.OneToOneField(
#         ReportHeader, on_delete=models.PROTECT, primary_key=True)
#     noon_report_type = models.ChoiceField(choices=NoonReportTypes.choices)
#     date_created = models.DateTimeField(auto_now_add=True)
#     date_modified = models.DateTimeField(auto_now=True)


# class NoonReportAtSea(models.model):
#     noon_report_header = models.OneToOneField(
#         NoonReportHeader, on_delete=models.PROTECT, primary_key=True)
#     distance_to_standby = models.FloatField(min=0.0)
#     hours_since_noon = models.FloatField(min=0.0)
#     hours_total = models.FloatField(min=0.0)
#     distance_obs_since_noon = models.FloatField(min=0.0)
#     distance_eng_since_noon = models.FloatField(min=0.0)
#     distance_eng_total = models.FloatField(min=0.0)
#     revolution_count = models.IntField(min=0.0)
#     since_noon_speed = models.FloatField(min=0.0)
#     since_noom_rpm = models.FloatField(min=0.0)
#     since_noon_slip = models.FloatField(min=0.0)
#     avg_speed = models.FloatField(min=0.0)
#     avg_rpm = models.FloatField(min=0.0)
#     avg_slip = models.FloatField(min=0.0)
#     weather = models.CharField()
#     sea_state = models.IntField(min=0)
#     wind_direction = models.FloatField(min=0.0, max=359.99)
#     wind_speed = models.FloatField()
#     heavy_weather_hours = models.FloatField(min=0.0)
#     heavy_weather_dist = models.FloatField(min=0.0)
#     heavy_weather_foc = models.FloatField(min=0.0)
#     heavy_weather_wind_direction = models.FloatField(min=0.0, max=359.99)
#     heavy_weather_wind_speed = models.FloatField(min=0.0)
#     heavy_weather_max_wave_ht = models.FloatField(min=0.0)
#     changed_speed = models.FloatField()
#     changed_foc = models.FloatField()
#     changed_rpm = models.FloatField()
#     changed_date = models.FloatField()
#     bunker_details = models., primary_key = True(BunkerDetails, on_delete=models.PROTECT, primary_key=False)
#     date_created = models.DateTimeField(auto_now_add=True)
#     date_modified = models.DateTimeField(auto_now=True)


# class BunkerDetails(models.model):
#     consumed_lsfo = models.FloatField(min=0.0)
#     consumed_mgo = models.FloatField(min=0.0)
#     consumed_correction = models.CharField()
#     consumed_remarks = models.CharField()
#     received_lsfo = models.FloatField(min=0.0)
#     received_lsfo_time = models.DateTimeField()
#     received_mgo = models.FloatField(min=0.0)
#     received_mgo_time = models.DateTimeField()
#     received_meslo = models.FloatField(min=0.0)
#     received_meclo = models.FloatField(min=0.0)
#     received_geslo = models.FloatField(min=0.0)
#     received_freshwater = models.FloatField(min=0.0)
#     received_correction = models.CharField()
#     received_remark = models.CharField()
#     rob_lsfo = models.FloatField(min=0.0)
#     rob_mgo = models.FloatField(min=0.0)
#     rob_freshwater = models.FloatField(min=0.0)
#     rob_meslo = models.FloatField(min=0.0)
#     rob_mest = models.FloatField(min=0.0)
#     rob_meslo = models.FloatField(min=0.0)
#     rob_ meclo = models.FloatField(min=0.0)
#     rob_ geslo = models.FloatField(min=0.0)
#     evaporated_freshwater = models.FloatField(min=0.0)
#     consumed_freshwater = models.FloatField(min=0.0)
#     date_created = models.DateTimeField(auto_now_add=True)
#     date_modified = models.DateTimeField(auto_now=True)
