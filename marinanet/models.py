from decimal import Decimal
import uuid

from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation
)
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.db import models as dmodels
from django.forms import ModelForm
# from timezone_field import TimeZoneField

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


class ShipSpecs(models.Model):
    ship = models.OneToOneField(Ship, on_delete=models.PROTECT)
    flag = models.CharField(max_length=127)
    deadweight_tonnage = models.DecimalField(max_digits=10, decimal_places=2)
    cargo_unit = models.CharField(max_length=50)
    fuel_options = models.JSONField()
    lubricating_oil_options = models.JSONField()
    machinery_options = models.JSONField()
    propeller_pitch = models.DecimalField(max_digits=3, decimal_places=1)

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


# def get_default_allowed_report_types():
#     return ['DSBY']


class Voyage(BaseModel):
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    voyage_num = models.PositiveIntegerField()
    # allowed_report_types = ArrayField(base_field=models.CharField(
    #     max_length=4), default=get_default_allowed_report_types)
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = "voyages"
        unique_together = ["ship", "voyage_num"]


class VoyageLeg(BaseModel):
    voyage = models.ForeignKey(Voyage, on_delete=models.PROTECT)
    leg_num = models.PositiveSmallIntegerField()
    departure_port = models.CharField(max_length=6)  # TODO: LOCODE
    departure_date = models.DateTimeField()
    depature_tz = models.FloatField()
    arrival_port = models.CharField(max_length=6)  # TODO: LOCODE
    arrival_date = models.DateTimeField()
    arrival_tz = models.FloatField()

    class Meta:
        db_table = "voyage_legs"


class ReportHeader(BaseModel):
    """Common header for all report types"""
    voyage_leg = models.ForeignKey(VoyageLeg, on_delete=models.PROTECT)
    report_type = models.CharField(max_length=4, choices=ReportTypes.choices)
    report_num = models.PositiveIntegerField()
    report_date = models.DateTimeField()
    report_tz = models.FloatField()
    # summer_time = models.BooleanField()
    # Note that for position, X is Longitude, Y is Latitude
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = "report_headers"


class ReportData(BaseModel):
    """Base model for all report data models"""
    report_header = models.OneToOneField(
        ReportHeader, on_delete=models.PROTECT, primary_key=True)

    class Meta:
        abstract = True


class TimeAndPosition(ReportData):
    """Base model for time and position models"""
    time = models.DateTimeField()
    timezone = models.FloatField()
    position = models.PointField(srid=4326)

    class Meta:
        abstract = True


class ReportRoute(ReportData):
    departure_port = models.CharField(max_length=6)  # TODO: LOCODE
    departure_date = models.DateTimeField()
    depature_tz = models.FloatField()
    arrival_port = models.CharField(max_length=6)  # TODO: LOCODE
    arrival_date = models.DateTimeField()
    arrival_tz = models.FloatField()

    class Meta:
        db_table = "report_routes"


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
    ice_condition = models.CharField(
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
    # max_wave_height = models.DecimalField(
    #     max_digits=3,
    #     decimal_places=1,
    #     validators=[
    #         MinValueValidator(Decimal("0.0"))])
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


class ConsumptionData(BaseModel):
    """Base model for consumption data"""
    ccdata = models.ForeignKey(
        ConsumptionConditionData, on_delete=models.PROTECT)

    class Meta:
        abstract = True


class ConsumptionDataCorrection(BaseModel):
    """Base model for consumption data correction"""
    correction = models.DecimalField(max_digits=7, decimal_places=2)
    remarks = models.TextField()

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


class FuelOilDataCorrection(ConsumptionDataCorrection):
    fuel_oil_data = models.OneToOneField(
        FuelOilData, on_delete=models.PROTECT, primary_key=True)

    class Meta:
        db_table = "fuel_oil_data_corrections"


class LubricatingOilData(ConsumptionData):
    fuel_oil_type = models.CharField(max_length=64)
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


class LubricatingOilDataCorrection(ConsumptionDataCorrection):
    lubricating_oil_data = models.OneToOneField(
        LubricatingOilData, on_delete=models.PROTECT, primary_key=True)

    class Meta:
        db_table = "lubricating_oil_data_corrections"


class FreshWaterData(BaseModel):
    ccdata = models.OneToOneField(
        ConsumptionConditionData, on_delete=models.PROTECT, primary_key=True)
    consumed = models.PositiveIntegerField()
    evaporated = models.PositiveIntegerField()
    received = models.PositiveIntegerField()
    discharged = models.PositiveIntegerField()
    rob = models.PositiveIntegerField()

    class Meta:
        db_table = "fresh_water_data"


class StoppageData(ReportData):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    duration = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))],
        null=True,
        blank=True)
    reduced_rpm = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0"))])
    position = models.PointField(srid=4326)
    reason = models.CharField(max_length=4)
    remarks = models.TextField()

    class Meta:
        db_table = "stoppage_data"


class CargoOperation(ReportData):
    pass


class DepartureVesselCondition(ReportData):
    pass


class DeparturePilotStation(ReportData):
    pass


class ArrivalPilotStation(ReportData):
    pass


class DepartureRunUp(ReportData):
    pass


class DistanceAndTime(ReportData):
    pass


class BudgetTransOcean(ReportData):
    pass


class PlannedOperation(ReportData):
    planned_operation_berth = models.BooleanField()
    planned_operation_stsstb = models.BooleanField()
    planned_operation_bunkering = models.BooleanField()
    planned_operation_drydocking = models.BooleanField()
    planned_operation_crewchange = models.BooleanField()
    planned_operation_provisions = models.BooleanField()
    planned_operation_survey = models.BooleanField()
    planned_operation_others = models.BooleanField()
    planned_operation_othersdetails = models.TextField()

    class Meta:
        db_table = "planned_operations"


class ActualPerformance(ReportData):
    pass


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
