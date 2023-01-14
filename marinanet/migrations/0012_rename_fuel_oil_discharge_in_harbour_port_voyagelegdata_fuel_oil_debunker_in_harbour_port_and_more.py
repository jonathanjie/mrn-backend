# Generated by Django 4.1.1 on 2023-01-14 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("marinanet", "0011_voyagelegdata_distance_eng_standby_to_cosp"),
    ]

    operations = [
        migrations.RenameField(
            model_name="voyagelegdata",
            old_name="fuel_oil_discharge_in_harbour_port",
            new_name="fuel_oil_debunker_in_harbour_port",
        ),
        migrations.RenameField(
            model_name="voyagelegdata",
            old_name="lube_oil_discharge_in_harbour_port",
            new_name="lube_oil_debunker_in_harbour_port",
        ),
        migrations.AlterField(
            model_name="voyagelegdata",
            name="freshwater_cons_in_harbour_port",
            field=models.PositiveIntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name="voyagelegdata",
            name="freshwater_discharge_in_harbour_port",
            field=models.PositiveIntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name="voyagelegdata",
            name="freshwater_gen_in_harbour_port",
            field=models.PositiveIntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name="voyagelegdata",
            name="freshwater_receipt_in_harbour_port",
            field=models.PositiveIntegerField(default=0, null=True),
        ),
    ]
