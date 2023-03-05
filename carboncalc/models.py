from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Q

from carboncalc.enums import (
    ApplicableCII,
    EnergyEfficiencyIndexType,
    EnginePowerLimitType,
    CIIFuelType,
    CIIGrade,
    CIIShipType,
    DCSMethod,
    FileAcceptanceStatus,
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

    energy_efficiency_index_type = models.CharField(
        max_length=4, choices=EnergyEfficiencyIndexType.choices)
    energy_efficiency_index_value = models.DecimalField(
        max_digits=6, decimal_places=3)

    is_engine_power_limited = models.BooleanField()
    engine_power_limit_type = models.CharField(
        max_length=4, choices=EnginePowerLimitType.choices, null=True, blank=True)
    engine_power_limit_value = models.IntegerField(null=True, blank=True)

    imo_dcs = models.BooleanField(default=True)
    imo_dcs_method = models.TextField(max_length=4, choices=DCSMethod.choices)

    eu_mrv = models.BooleanField(default=False)
    eu_mrv_method = models.CharField(
        max_length=4, choices=MRVMethod.choices, null=True, blank=True)

    applicable_cii = models.CharField(
        max_length=8, choices=ApplicableCII.choices)
    trial_cii_types = ArrayField(
        models.CharField(max_length=8, choices=TrialCII.choices),
        default=list)

    fuel_options = ArrayField(
        models.CharField(
            max_length=4,
            choices=CIIFuelType.choices),
        default=list)

    class Meta:
        db_table = "cii_configs"
        # constraints = [
        #     models.CheckConstraint(
        #         check=Q(eu_mrv_method__isnull=False) | Q(eu_mrv=False),
        #         name="eu_mrv_details_null_check"
        #     ),
        #     models.CheckConstraint(
        #         check=((
        #             Q(engine_power_limit_type__isnull=False) &
        #             Q(engine_power_limit_value__isnull=False)) |
        #             Q(is_engine_power_limited=False)),
        #         name="engine_power_limit_details_null_check",
        #     ),
        # ]


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

    def get_boundary_for_grade(self, grade: str) -> str:
        if grade == CIIGrade.A:
            return self.boundary_a
        elif grade == CIIGrade.B:
            return self.boundary_b
        elif grade == CIIGrade.C:
            return self.boundary_c
        elif grade == CIIGrade.D:
            return self.boundary_d
        else:
            return Decimal("Infinity")


class StandardizedDataReportingFile(BaseS3FileModel):
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    year = models.PositiveSmallIntegerField()
    acceptance_status = models.CharField(
        max_length=15, choices=FileAcceptanceStatus.choices,
        default=FileAcceptanceStatus.PROCESSING)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "standardized_data_reporting_file"
        constraints = [
            models.UniqueConstraint(
                fields=('ship', 'year'),
                name='standardizeddatareportingfile_ship_year'
            ),
        ]


class StandardizedDataReportingData(BaseModel):
    reporting_file = models.ForeignKey(
        StandardizedDataReportingFile, on_delete=models.CASCADE)
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    year = models.PositiveSmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    gross_tonnage = models.DecimalField(max_digits=10, decimal_places=2)
    deadweight_tonnage = models.DecimalField(max_digits=10, decimal_places=2)
    total_hours = models.DecimalField(max_digits=7, decimal_places=3)
    total_distance = models.DecimalField(max_digits=8, decimal_places=2)
    fuel_oil_burned = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)


class EnergyEfficiencyTechnicalFile(BaseS3FileModel):
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    energy_efficiency_index_type = models.CharField(
        max_length=4, choices=EnergyEfficiencyIndexType.choices)
