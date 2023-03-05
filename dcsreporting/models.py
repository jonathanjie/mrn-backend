from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from core.models import (
    BaseModel,
    BaseS3FileModel,
    Ship,
)
from dcsreporting.enums import DCSType


class DCSUploadedFile(BaseS3FileModel):
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    year = models.PositiveSmallIntegerField()
    dcs_type = models.PositiveSmallIntegerField(
        choices=DCSType.choices,
        default=DCSType.TYPE_1)

    class Meta:
        db_table = "dcs_uploaded_files"


class DCSVoyage(BaseModel):
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    year = models.PositiveSmallIntegerField()

    voyage_num = models.CharField(max_length=7)
    departure_port = models.CharField(max_length=7)
    departure_date = models.DateTimeField()
    departure_cargo_operation = models.BooleanField()
    arrival_port = models.CharField(max_length=7)
    arrival_date = models.DateTimeField()
    time_at_sea = models.DecimalField(max_digits=5, decimal_places=1)
    distance_travelled = models.DecimalField(max_digits=5, decimal_places=1)
    time_idle_at_anchorage = models.DecimalField(
        max_digits=5, decimal_places=1)
    cargo_carried_passenger = models.DecimalField(
        max_digits=8, decimal_places=2)
    cargo_carried_weight_volume = models.DecimalField(
        max_digits=8, decimal_places=2)
    transport_work_passenger = models.DecimalField(
        max_digits=13, decimal_places=3)
    transport_work_weight_volume = models.DecimalField(
        max_digits=13, decimal_places=3)
    rob_at_departure = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)
    rob_at_arrival = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)
    at_berth_consumption = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)
    net_consumption = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)
    bunkering_before_arrival = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)
    bunkering_after_arrival = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)
    debunkering_before_arrival = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)
    debunkering_after_arrival = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)
    correction_time_at_sea = models.DecimalField(
        max_digits=5, decimal_places=1)
    correction_distance_travelled = models.DecimalField(
        max_digits=5, decimal_places=1)
    correction_consumption = models.JSONField(
        default=dict, encoder=DjangoJSONEncoder)

    class Meta:
        db_table = "dcs_voyages"

    """
    voyage_num
    departure_port
    departure_date
    departure_cargo_operation
    arrival_port
    arrival_date
    time_at_sea
    distance_travelled
    time_idle_at_anchorage
    cargo_carried_passenger
    cargo_carried_weight_volume
    transport_work_passenger
    transport_work_weight_volume
    rob_at_departure
    rob_at_arrival
    at_berth_consumption
    net_consumption
    bunkering_before_arrival
    bunkering_after_arrival
    debunkering_before_arrival
    debunkering_after_arrival
    correction_time_at_sea
    correction_distance_travelled
    correction_consumption
    """
