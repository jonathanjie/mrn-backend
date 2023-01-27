from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator


from core.models import (
    BaseModel,
    Company,
    User,
)
from marinanet.enums import (
    FuelType,
    ShipAccessPrivilege,
    ShipType,
    Status,
)


class Ship(BaseModel):
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
