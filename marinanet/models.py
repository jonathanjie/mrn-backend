from django.db import models

from auth.models import User
from enum import Status, ShipAccessPrivilege


class Company(models.Model):
    name = models.CharField(max_length=255)
    link = models.UrlField()
    status = models.IntegerField(choices=Status.choices)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "companies"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT,
        primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    role = models.CharField(max_length=255)
    status = models.IntegerField(choices=Status.choices)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "profiles"


class Ship(models.Model):
    name = models.CharField(max_length=255)
    imo_reg = models.IntegerField()
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    status = models.IntegerField(choices=Status.choices)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    assigned_users = models.ManyToManyField(
        Person,
        through = 'ShipUser',
        through_fields = ('ship', 'user')
    )

    class Meta:
        db_table = "ships"


class ShipUser(models.Model):
    ship = models.ForeignKey(Ship, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    privilege = models.ChoiceField(choices=Ship.choices)
    status = models.IntegerField(choices=Status.choices)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
