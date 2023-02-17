from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Q

from carboncalc.enums import (
    EnergyEfficiencyIndexType,
    CIIGrade,
    CIIShipType,
    ApplicableCII,
    DCSMethod,
    MRVMethod,
    TrialCII,
)
from core.models import (
    BaseModel,
    BaseS3FileModel,
    Ship,
)


class CIIConfig(BaseModel):
    ship = models.OneToOneField(Ship, on_delete=models.PROTECT)

    energy_efficiency_index_type = models.TextField()
    energy_efficiency_index_value = models.DecimalField(
        max_digits=6, decimal_places=3)

    is_engine_power_limited = models.BooleanField()
    engine_power_limit_type = models.TextField(
        max_length=4, null=True)
    engine_power_limit_value = models.IntegerField(null=True)

    imo_dcs = models.BooleanField(default=True)
    imo_dcs_method = models.TextField(max_length=4, choices=DCSMethod.choices)

    eu_mrv = models.BooleanField(default=False)
    eu_mrv_method = models.TextField(
        max_length=4, choices=MRVMethod.choices, null=True)

    applcable_cii = models.TextField(
        max_length=8, choices=ApplicableCII.choices)
    trial_cii_types = ArrayField(
        models.CharField(max_length=8, choices=TrialCII.choices),
        default=list)

    class Meta:
        db_table = "cii_configs"
        constraints = [
            models.CheckConstraint(
                check=Q(eu_mrv_method__isnull=False) | Q(eu_mrv=False),
                name="eu_mrv_details_null_check"
            ),
            models.CheckConstraint(
                check=((
                    Q(engine_power_limit_type__isnull=False) &
                    Q(engine_power_limit_value__isnull=False)) |
                    Q(engine_power_limited=False)),
                name="engine_power_limit_details_null_check",
            ),
        ]


class TargetCII(BaseModel):
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    year = models.PositiveSmallIntegerField()
    grade = models.TextField(max_length=1, choices=CIIGrade.choices)

    class Meta:
        db_table = "target_ciis"
        constraints = [
            models.UniqueConstraint(
                fields=('ship', 'year'),
                name='targetcii_ship_year'
            ),
        ]


class CalculatedCII(BaseModel):
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    year = models.PositiveSmallIntegerField()
    value = models.DecimalField(max_digits=6, decimal_places=3)
    grade = models.TextField(max_length=1, choices=CIIGrade.choices)

    class Meta:
        db_table = "calculated_ciis"
        constraints = [
            models.UniqueConstraint(
                fields=('ship', 'year'),
                name='calculatedcii_ship_year'
            ),
        ]


class CIIRawData(BaseModel):
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    year = models.PositiveSmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    distance_sailed = models.PositiveIntegerField()
    fuel_oil_burned = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)

    class Meta:
        db_table = "cii_raw_data"
        constraints = [
            models.UniqueConstraint(
                fields=('ship', 'year'),
                name='ciirawdata_ship_year'
            ),
        ]


class CIIShipYearBoundaries(BaseModel):
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    year = models.PositiveSmallIntegerField()
    boundary_a = models.DecimalField(max_digits=6, decimal_places=3)
    boundary_b = models.DecimalField(max_digits=6, decimal_places=3)
    boundary_c = models.DecimalField(max_digits=6, decimal_places=3)
    boundary_d = models.DecimalField(max_digits=6, decimal_places=3)

    class Meta:
        db_table = "cii_ship_year_boundaries"
        constraints = [
            models.UniqueConstraint(
                fields=('ship', 'year'),
                name='ciishipyearboundaries_ship_year'
            ),
        ]


class StandardizedDataReportingFile(BaseS3FileModel):
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    year = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "standardized_data_reporting_file"
        constraints = [
            models.UniqueConstraint(
                fields=('ship', 'year'),
                name='standardizeddatareportingfile_ship_year'
            ),
        ]
