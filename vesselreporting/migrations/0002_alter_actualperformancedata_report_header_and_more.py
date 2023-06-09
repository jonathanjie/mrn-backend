# Generated by Django 4.1.1 on 2023-03-05 16:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("vesselreporting", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="actualperformancedata",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="additionalremarks",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="arrivalfwetimeandposition",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="arrivalpilotstation",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="arrivalstandbytimeandposition",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="bdndata",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="cargooperation",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="consumptionconditiondata",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="departurepilotstation",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="departurerunup",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="departurevesselcondition",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="distancetimedata",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="eventdata",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="heavyweatherdata",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="noonreporttimeandposition",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="performancedata",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="plannedoperations",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="portoperations",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="reportroute",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="sailingplan",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="stoppagedata",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="totalconsumptiondata",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="weatherdata",
            name="report_header",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="vesselreporting.reportheader",
            ),
        ),
    ]
