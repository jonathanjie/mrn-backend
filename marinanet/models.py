from decimal import Decimal
import uuid

from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MaxValueValidator, MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
# from timezone_field import TimeZoneField

from auth0.models import User
from marinanet.enums import (
    ActualPerformanceType,
    Cardinal_8,
    Cardinal_16,
    ConsumptionType,
    DouglasScale,
    FuelType,
    GlacierIceCondition,
    LoadCondition,
    ParkingStatus,
    ReportType,
    ShipAccessPrivilege,
    ShipType,
    Status,
    StoppageReason,
    SwellScale,
    TotalConsumptionType,
    Weather,
)


class BaseModel(models.Model):
    """Base Model to be used for all subsequent models"""
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


""" USER MODELS
"""


class Company(BaseModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
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
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.PROTECT, primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    role = models.CharField(max_length=255)
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = "profiles"


class Ship(BaseModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255)
    imo_reg = models.PositiveIntegerField(
        unique=True,
        validators=[
            MinValueValidator(1000000),
            MaxValueValidator(9999999)])     # 7 digits
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    ship_type = models.CharField(max_length=4, choices=ShipType.choices)
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


class ShipSpecs(models.Model):
    ship = models.OneToOneField(Ship, on_delete=models.PROTECT)
    flag = models.CharField(max_length=127)
    deadweight_tonnage = models.DecimalField(max_digits=10, decimal_places=2)
    cargo_unit = models.CharField(max_length=50)
    fuel_options = ArrayField(
        models.CharField(
            max_length=4,
            choices=FuelType.choices),
        default=list)
    lubricating_oil_options = ArrayField(
        models.CharField(max_length=64),
        default=list)
    machinery_options = ArrayField(
        models.CharField(max_length=64),
        default=list)
    propeller_pitch = models.DecimalField(max_digits=5, decimal_places=4)

    class Meta:
        db_table = "ship_specs"
        verbose_name_plural = "ship_specs"


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
        unique_together = ["ship", "voyage_num"]


class VoyageLeg(BaseModel):
    voyage = models.ForeignKey(Voyage, on_delete=models.PROTECT)
    leg_num = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "voyage_legs"


class VoyageLegData(BaseModel):
    voyage_leg = models.OneToOneField(
        VoyageLeg, on_delete=models.PROTECT, null=True)
    last_report_type = models.CharField(
        max_length=4, choices=ReportType.choices, null=True)
    last_report_date = models.DateTimeField(null=True)
    last_report_tz = models.FloatField(null=True)

    departure_port = models.CharField(max_length=6, null=True)  # TODO: LOCODE
    departure_date = models.DateTimeField(null=True)
    departure_tz = models.FloatField(null=True)
    arrival_port = models.CharField(max_length=6, null=True)  # TODO: LOCODE
    arrival_date = models.DateTimeField(null=True)
    arrival_tz = models.FloatField(null=True)

    displacement_at_departure = models.DecimalField(
        max_digits=7,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))],
        null=True)
    cargo_total_at_departure = models.PositiveIntegerField(null=True)
    load_condition = models.CharField(
        max_length=16,
        choices=LoadCondition.choices,
        null=True)
    propeller_pitch = models.DecimalField(
        max_digits=3, decimal_places=1, null=True)

    total_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        null=True)
    time_standby_to_cosp = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))],
        null=True)
    time_stopped_at_sea = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        null=True)
    distance_standby_to_cosp = models.DecimalField(
        max_digits=3,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))],
        null=True)
    distance_observed_total = models.DecimalField(
        max_digits=5,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))],
        null=True)
    distance_engine_total = models.DecimalField(
        max_digits=5,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))],
        null=True)
    revolution_count = models.IntegerField(
        validators=[MinValueValidator(0)], null=True)
    revolution_count_standby_to_cosp = models.IntegerField(
        validators=[MinValueValidator(0)], null=True)
    distance_to_go = models.DecimalField(
        max_digits=5,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))],
        null=True)
    speed_average = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))],
        null=True)
    rpm_average = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))],
        null=True)
    slip_average = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))],
        null=True)

    fuel_oil_robs = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)
    fuel_oil_cons_port_to_port = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)
    fuel_oil_cons_pilot_to_pilot = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)
    fuel_oil_cons_in_harbour_port = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)
    lube_oil_robs = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)
    freshwater_rob = models.PositiveIntegerField(null=True)

    planned_operations = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)
    last_operation = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)
    parking_status = models.CharField(
        max_length=32,
        choices=ParkingStatus.choices,
        null=True)

    class Meta:
        db_table = "voyage_leg_data"


class ReportHeader(BaseModel):
    """Common header for all report types"""
    voyage_leg = models.ForeignKey(VoyageLeg, on_delete=models.PROTECT)
    report_type = models.CharField(max_length=4, choices=ReportType.choices)
    report_num = models.PositiveIntegerField()
    report_date = models.DateTimeField()
    report_tz = models.FloatField()
    # summer_time = models.BooleanField()
    # Note that for position, X is Longitude, Y is Latitude
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = "report_headers"


class ReportDataBaseModel(BaseModel):
    """Base model for all report data models"""
    report_header = models.OneToOneField(
        ReportHeader, on_delete=models.PROTECT, primary_key=True)

    class Meta:
        abstract = True


class TimeAndPositionBaseModel(ReportDataBaseModel):
    """Base model for time and position models"""
    time = models.DateTimeField()
    timezone = models.FloatField()
    position = models.PointField(srid=4326)

    class Meta:
        abstract = True


class NoonReportTimeAndPosition(TimeAndPositionBaseModel):
    class Meta:
        db_table = "noon_report_time_and_position"


class ReportRoute(ReportDataBaseModel):
    departure_port = models.CharField(max_length=6)  # TODO: LOCODE
    departure_date = models.DateTimeField()
    departure_tz = models.FloatField()
    arrival_port = models.CharField(max_length=6)  # TODO: LOCODE
    arrival_date = models.DateTimeField()
    arrival_tz = models.FloatField()

    class Meta:
        db_table = "report_routes"


class WeatherData(ReportDataBaseModel):
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
    ice_condition = models.CharField(
        max_length=4,
        choices=GlacierIceCondition.choices,
        default=GlacierIceCondition.NONE)

    class Meta:
        db_table = "weather_data"


class HeavyWeatherData(ReportDataBaseModel):
    weather_notation = models.CharField(max_length=2, choices=Weather.choices)
    total_hours = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))])
    observed_distance = models.DecimalField(
        max_digits=4,
        decimal_places=1,
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
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "heavy_weather_data"


class DistanceTimeData(ReportDataBaseModel):
    hours_since_last = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("48"))])
    hours_total = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))])
    distance_to_go = models.DecimalField(
        max_digits=5,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))])
    remarks_for_changes = models.TextField()
    distance_observed_since_last = models.DecimalField(
        max_digits=3,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))])
    distance_observed_total = models.DecimalField(
        max_digits=5,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))])
    distance_engine_since_last = models.DecimalField(
        max_digits=3,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))])
    distance_engine_total = models.DecimalField(
        max_digits=5,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))])
    revolution_count = models.IntegerField(
        validators=[MinValueValidator(0)])
    set_rpm = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))],
        null=True)

    class Meta:
        db_table = "distance_time_data"


class PerformanceData(ReportDataBaseModel):
    speed_since_last = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    rpm_since_last = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    slip_since_last = models.DecimalField(
        max_digits=4,
        decimal_places=2)
    speed_average = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    rpm_average = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    slip_average = models.DecimalField(
        max_digits=4,
        decimal_places=2)

    class Meta:
        db_table = "performance_data"


class ConsumptionConditionData(ReportDataBaseModel):
    consumption_type = models.CharField(
        max_length=16, choices=ConsumptionType.choices)

    class Meta:
        db_table = "consumption_conduiion_data"
        unique_together = ["report_header", "consumption_type"]


class ConsumptionDataBaseModel(BaseModel):
    """Base model for consumption data"""
    ccdata = models.ForeignKey(
        ConsumptionConditionData, on_delete=models.PROTECT)

    class Meta:
        abstract = True


class ConsumptionDataCorrectionBaseModel(BaseModel):
    """Base model for consumption data correction"""
    correction = models.DecimalField(max_digits=7, decimal_places=2)
    remarks = models.TextField()

    class Meta:
        abstract = True


class FuelOilData(ConsumptionDataBaseModel):
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
    breakdown = models.JSONField(encoder=DjangoJSONEncoder)

    class Meta:
        db_table = "fuel_oil_data"


class FuelOilDataCorrection(ConsumptionDataCorrectionBaseModel):
    fuel_oil_data = models.OneToOneField(
        FuelOilData, on_delete=models.PROTECT, primary_key=True)

    class Meta:
        db_table = "fuel_oil_data_corrections"


class LubricatingOilData(ConsumptionDataBaseModel):
    lubricating_oil_type = models.CharField(max_length=64)
    total_consumption = models.DecimalField(
        blank=True,
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    receipt = models.DecimalField(
        blank=True,
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    debunkering = models.DecimalField(
        blank=True,
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    rob = models.DecimalField(
        blank=True,
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])

    class Meta:
        db_table = "lubricating_oil_data"


class LubricatingOilDataCorrection(ConsumptionDataCorrectionBaseModel):
    lubricating_oil_data = models.OneToOneField(
        LubricatingOilData, on_delete=models.PROTECT, primary_key=True)

    class Meta:
        db_table = "lubricating_oil_data_corrections"


class FreshWaterData(BaseModel):
    ccdata = models.OneToOneField(
        ConsumptionConditionData, on_delete=models.PROTECT, primary_key=True)
    consumed = models.PositiveIntegerField()
    generated = models.PositiveIntegerField()
    received = models.PositiveIntegerField()
    discharged = models.PositiveIntegerField()
    rob = models.PositiveIntegerField()

    class Meta:
        db_table = "fresh_water_data"


class StoppageData(ReportDataBaseModel):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    duration = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        null=True,
        blank=True)
    reduced_rpm = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    position = models.PointField(srid=4326)
    reason = models.CharField(max_length=16, choices=StoppageReason.choices)
    remarks = models.TextField()

    class Meta:
        db_table = "stoppage_data"


class CargoOperation(ReportDataBaseModel):
    load_condition = models.CharField(
        max_length=16,
        choices=LoadCondition.choices)
    loading = models.PositiveIntegerField()
    unloading = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    time = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))])

    class Meta:
        db_table = "cargo_operations"


class DepartureVesselCondition(ReportDataBaseModel):
    draft_fwd = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    draft_mid = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    draft_aft = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    constant = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    gm = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    ballast = models.DecimalField(
        max_digits=7,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    displacement = models.DecimalField(
        max_digits=7,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])

    class Meta:
        db_table = "departure_vessel_conditions"


class PilotStation(ReportDataBaseModel):
    """Base model for pilot stations"""
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    position = models.PointField(srid=4326)

    class Meta:
        abstract = True


class DeparturePilotStation(PilotStation):
    class Meta:
        db_table = "departure_pilot_stations"


class ArrivalPilotStation(PilotStation):
    draft_fwd = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    draft_mid = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    draft_aft = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])

    class Meta:
        db_table = "arrival_pilot_stations"


class DepartureRunUp(TimeAndPositionBaseModel):
    class Meta:
        db_table = "departure_runups"


# class DistanceTimeData(ReportDataBaseModel):
#     time = models.PositiveSmallIntegerField()
#     distance_obs = models.DecimalField(
#         max_digits=3,
#         decimal_places=0,
#         validators=[MinValueValidator(Decimal("0.0"))])
#     distance_eng = models.DecimalField(
#         max_digits=3,
#         decimal_places=0,
#         validators=[MinValueValidator(Decimal("0.0"))])
#     revolution_count = models.IntegerField(
#         validators=[MinValueValidator(0)])
#     set_rpm = models.DecimalField(
#         max_digits=4,
#         decimal_places=1,
#         validators=[MinValueValidator(Decimal("0.0"))])

#     class Meta:
#         db_table = "distance_time_data"


class SailingPlan(ReportDataBaseModel):
    distance_to_go = models.DecimalField(
        max_digits=5,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))])
    speed = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    me_daily_fo_consumption = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    me_rpm = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])

    class Meta:
        db_table = "sailing_plans"


class ArrivalStandbyTimeAndPosition(TimeAndPositionBaseModel):
    class Meta:
        db_table = "arrival_standby_time_and_position"


class PlannedOperations(ReportDataBaseModel):
    cargo_operation_berth = models.BooleanField()
    cargo_operation_stsstb = models.BooleanField()
    bunkering_debunkering = models.BooleanField()
    dry_docking = models.BooleanField()
    crew_change = models.BooleanField()
    receiving_provisions_spares = models.BooleanField()
    surveying = models.BooleanField()
    others = models.BooleanField()
    planned_operation_othersdetails = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "planned_operations"


class ActualPerformanceData(ReportDataBaseModel):
    actual_performance_type = models.CharField(
        max_length=16,
        choices=ActualPerformanceType.choices)
    distance_obs_total = models.DecimalField(
        max_digits=5,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("0.0"))])
    sailing_time = models.PositiveIntegerField()
    displacement = models.DecimalField(
        max_digits=7,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    speed_average = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    rpm_average = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    me_average_daily_fo_consumption = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])

    class Meta:
        db_table = "actual_performance_data"


class TotalConsumptionData(ReportDataBaseModel):
    consumption_type = models.CharField(
        max_length=16,
        choices=TotalConsumptionType.choices)

    class Meta:
        db_table = "total_consumption_data"


class TotalConsumptionDataBaseModel(BaseModel):
    """Base model for consumption data"""
    tcdata = models.ForeignKey(TotalConsumptionData, on_delete=models.PROTECT)

    class Meta:
        abstract = True


class FuelOilTotalConsumptionData(TotalConsumptionDataBaseModel):
    fuel_oil_type = models.CharField(max_length=4, choices=FuelType.choices)
    total_consumption = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    receipt = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))],
        default=0.0)
    debunkering = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))],
        default=0.0)
    rob = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    breakdown = models.JSONField(encoder=DjangoJSONEncoder)

    class Meta:
        db_table = "fuel_oil_total_consumption_data"


class FuelOilTotalConsumptionDataCorrection(ConsumptionDataCorrectionBaseModel):
    fuel_oil_tcdata = models.OneToOneField(
        FuelOilTotalConsumptionData,
        on_delete=models.PROTECT,
        primary_key=True)

    class Meta:
        db_table = "fuel_oil_total_consumption_data_corrections"


class LubricatingOilTotalConsumptionData(TotalConsumptionDataBaseModel):
    lubricating_oil_type = models.CharField(max_length=64)
    total_consumption = models.DecimalField(
        blank=True,
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    receipt = models.DecimalField(
        blank=True,
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))],
        default=0.0)
    debunkering = models.DecimalField(
        blank=True,
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))],
        default=0.0)
    rob = models.DecimalField(
        blank=True,
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])

    class Meta:
        db_table = "lubricating_oil_total_consumption_data"


class LubricatingOilTotalConsumptionDataCorrection(ConsumptionDataCorrectionBaseModel):
    lubricating_oil_tcdata = models.OneToOneField(
        LubricatingOilTotalConsumptionData,
        on_delete=models.PROTECT,
        primary_key=True)

    class Meta:
        db_table = "lubricating_oil_total_consumption_data_corrections"


class FreshWaterTotalConsumptionData(BaseModel):
    tcdata = models.OneToOneField(
        TotalConsumptionData, on_delete=models.PROTECT, primary_key=True)
    consumed = models.PositiveIntegerField()
    generated = models.PositiveIntegerField()
    received = models.PositiveIntegerField()
    discharged = models.PositiveIntegerField()
    rob = models.PositiveIntegerField()

    class Meta:
        db_table = "fresh_water_total_consumption_data"


class ArrivalFWETimeAndPosition(TimeAndPositionBaseModel):
    parking_status = models.CharField(
        max_length=32,
        choices=ParkingStatus.choices)

    class Meta:
        db_table = "arrival_fwe_time_and_position"


class PortOperations(ReportDataBaseModel):
    waiting = models.BooleanField()
    cargo_operation = models.BooleanField()
    bunkering_debunkering = models.BooleanField()
    others = models.BooleanField()
    others_details = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "port_operations"


class EventData(TimeAndPositionBaseModel):
    distance_travelled = models.PositiveSmallIntegerField()
    parking_status = models.CharField(
        max_length=32,
        choices=ParkingStatus.choices)

    class Meta:
        db_table = "event_data"


class BDNData(ReportDataBaseModel):
    bunkering_port = models.CharField(max_length=6)
    bunkering_date = models.DateTimeField()
    bdn_file = ArrayField(models.URLField(max_length=1500))
    delivered_oil_type = models.CharField(max_length=64)
    delivered_quantity = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))])
    density_15 = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0.0"))])
    specific_gravity_15 = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0.0"))])
    viscosity_value = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.0"))])
    viscosity_temperature = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    flash_point = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.0"))])
    sulfur_content = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.0"))])
    sample_sealing_marpol = models.CharField(max_length=64)
    sample_sealing_ship = models.CharField(max_length=64)
    sample_sealing_barge = models.CharField(max_length=64)
    alongside_date = models.DateTimeField()
    hose_connection_date = models.DateTimeField()
    pump_start_date = models.DateTimeField()
    pump_stop_date = models.DateTimeField()
    hose_disconnection_date = models.DateTimeField()
    slipoff_date = models.DateTimeField()
    purchaser = models.CharField(max_length=128)
    barge_name = models.CharField(max_length=128)
    supplier_name = models.CharField(max_length=128)
    supplier_address = models.TextField()
    supplier_contact = PhoneNumberField()


# ======== FOR LATER =========
# class ShipSpecs(models.Model):
#     ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
#     owner = models.CharField(max_length=127)
#     commercial_manager = models.CharField(max_length=127)
#     technical_manager = models.CharField(max_length=127)
#     yard = models.CharField(max_length=127)
#     delivery_date = models.DateField()
#     flag = models.CharField(max_length=127)
#     registry_port = models.CharField(max_length=127)
#     call_sign = models.CharField(max_length=15)
#     mmsi = models.CharField(max_length=15)
#     hull_no = models.CharField(max_length=15)
#     class_society = models.CharField(max_length=31)
#     next_drydock_date = models.DateField()
#     loa = models.DecimalField(max_digits=5, decimal_places=2)
#     dimensions = models.JSONField()
#     draft = models.DecimalField(max_digits=5, decimal_places=2)
#     gross_tonnage = models.DecimalField(max_digits=5, decimal_places=2)
#     net_tonnage = models.DecimalField(max_digits=5, decimal_places=2)
#     deadweight_tonnage = models.DecimalField(max_digits=5, decimal_places=2)
#     full_displacement = models.DecimalField(max_digits=5, decimal_places=2)
#     cargo_capacity = models.DecimalField(max_digits=5, decimal_places=2)
#     lightship_weight = models.DecimalField(max_digits=5, decimal_places=2)
#     cruising_range = models.DecimalField(max_digits=10, decimal_places=2)
#     sea_trial_speed = models.DecimalField(max_digits=5, decimal_places=2)
#     design_draft = models.DecimalField(max_digits=5, decimal_places=2)
#     service_speed = models.DecimalField(max_digits=5, decimal_places=2)
#     speed_table = models.JSONField()
#     avg_daily_fuel_consumption = models.DecimalField(max_digits=5, decimal_places=2)
#     ballast_daily_fuel_consumption = models.DecimalField(max_digits=5, decimal_places=2)
#     laden_daily_fuel_consumption = models.DecimalField(max_digits=5, decimal_places=2)

#     # Move to separate engine table
#     main_engine_type = models.CharField(max_length=127)
#     main_engine_manufacturer = models.CharField(max_length=127)
#     main_engine_mcr = models.DecimalField(max_digits=10, decimal_places=2)
#     main_engine_imo_tier = models.CharField(max_length=1)
#     main_engine_count = models.IntegerField()
#     main_engine_fuel_type = models.CharField(max_length=127)
#     generator_type = models.CharField(max_length=127)
#     generator_manufacturer = models.CharField(max_length=127)
#     generator_rpm = models.IntegerField()
#     generator_mcr = models.DecimalField(max_digits=5, decimal_places=2)
#     generator_count = models.IntegerField()
#     generator_fuel_type = models.DecimalField(max_digits=5, decimal_places=2)
#     boiler_type = models.CharField(max_length=127)
#     boiler_capacity = models.CharField(max_length=127)
#     boiler_count = models.IntegerField()

#     propeller_type = models.CharField(max_length=127)
#     propeller_blades = models.IntegerField()
#     propeller_diameter = models.IntegerField()
#     propeller_count = models.IntegerField()
#     bwts_is_fitted = models.BooleanField()
#     scrubber_is_installed = models.BooleanField()
#     scr_is_installed = models.BooleanField()
#     egr_is_installed = models.BooleanField()
#     cargo_tanks = models.JSONField()
#     caro_tank_specs = models.JSONField()
#     cargo_pump = models.JSONField()
#     cargo_tank_coating = models.CharField(max_length=127)

#     cargo_capacity = models.DecimalField(max_digits=5, decimal_places=2)
#     cargo_pump_type = models.CharField(max_length=127)
#     cargo_pump_capacity = models.DecimalField(max_digits=5, decimal_places=2)
#     cargo_pump_set = models.IntegerField()
#     windlass_is_installed = models.BooleanField()
#     hose_handling_crane_is_installed = models.BooleanField()
#     water_ballast_capacity = models.DecimalField(max_digits=5, decimal_places=2)
#     hfo_capacity = models.DecimalField(max_digits=5, decimal_places=2)
#     mdo_lsmgo_capacity = models.DecimalField(max_digits=5, decimal_places=2)
#     freshwater_capacity = models.DecimalField(max_digits=5, decimal_places=2)
#     eexi_rating = models.CharField(max_length=1)
#     estimated_cii_rating = models.CharField(max_length=1)

#     class Meta:
#         db_table = "ship_specs"
