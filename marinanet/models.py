import uuid
from django.db import models

class Ship(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=100, help_text='Name of the Ship')
    imo_reg_num = models.CharField(max_length=20, help_text='IMO Registration Number')
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True)
    ship_type = models.CharField(max_length=10) ## TODO: add enum & choices https://stackoverflow.com/questions/54802616/how-to-use-enums-as-a-choice-field-in-django-model

