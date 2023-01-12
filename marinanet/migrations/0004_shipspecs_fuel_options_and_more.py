# Generated by Django 4.1.1 on 2023-01-12 07:17

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("marinanet", "0003_remove_shipspecs_fuel_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="shipspecs",
            name="fuel_options",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    choices=[
                        ("HFO", "HFO"),
                        ("LSFO", "LSFO"),
                        ("MDO", "MDO"),
                        ("MGO", "MGO"),
                        ("LPGP", "LPG (Propane)"),
                        ("LPGB", "LPG (Butane"),
                        ("METH", "Methanol"),
                        ("ETH", "Ethanol"),
                        ("LNG", "LNG"),
                    ],
                    max_length=4,
                ),
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="shipspecs",
            name="lubricating_oil_options",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=64), default=list, size=None
            ),
        ),
        migrations.AddField(
            model_name="shipspecs",
            name="machinery_options",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=64), default=list, size=None
            ),
        ),
    ]
