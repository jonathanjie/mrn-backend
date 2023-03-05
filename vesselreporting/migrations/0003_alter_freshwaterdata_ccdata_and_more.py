# Generated by Django 4.1.1 on 2023-03-05 16:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("vesselreporting", "0002_alter_actualperformancedata_report_header_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="freshwaterdata",
            name="ccdata",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.consumptionconditiondata",
            ),
        ),
        migrations.AlterField(
            model_name="freshwatertotalconsumptiondata",
            name="tcdata",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.totalconsumptiondata",
            ),
        ),
        migrations.AlterField(
            model_name="fueloildata",
            name="ccdata",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="vesselreporting.consumptionconditiondata",
            ),
        ),
        migrations.AlterField(
            model_name="fueloildatacorrection",
            name="fuel_oil_data",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.fueloildata",
            ),
        ),
        migrations.AlterField(
            model_name="fueloiltotalconsumptiondata",
            name="tcdata",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="vesselreporting.totalconsumptiondata",
            ),
        ),
        migrations.AlterField(
            model_name="fueloiltotalconsumptiondatacorrection",
            name="fuel_oil_tcdata",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.fueloiltotalconsumptiondata",
            ),
        ),
        migrations.AlterField(
            model_name="lubricatingoildata",
            name="ccdata",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="vesselreporting.consumptionconditiondata",
            ),
        ),
        migrations.AlterField(
            model_name="lubricatingoildatacorrection",
            name="lubricating_oil_data",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.lubricatingoildata",
            ),
        ),
        migrations.AlterField(
            model_name="lubricatingoiltotalconsumptiondata",
            name="tcdata",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="vesselreporting.totalconsumptiondata",
            ),
        ),
        migrations.AlterField(
            model_name="lubricatingoiltotalconsumptiondatacorrection",
            name="lubricating_oil_tcdata",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.lubricatingoiltotalconsumptiondata",
            ),
        ),
    ]
