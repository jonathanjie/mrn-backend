# Generated by Django 4.1.1 on 2023-02-24 16:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("vesselreporting", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reportedge",
            name="next_report",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="report_edge_backward",
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="reportedge",
            name="previous_report",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="report_edge_forward",
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="voyagelegprogress",
            name="arrival_eosp",
            field=models.OneToOneField(
                limit_choices_to={"report_type": "ASBY"},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="voyagelegprogress",
            name="arrival_fwe",
            field=models.OneToOneField(
                limit_choices_to={"report_type": "AFWE"},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="voyagelegprogress",
            name="departure_cosp",
            field=models.OneToOneField(
                limit_choices_to={"report_type": "DCSP"},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="voyagelegprogress",
            name="departure_standby",
            field=models.OneToOneField(
                limit_choices_to={"report_type": "DSBY"},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="vesselreporting.reportheader",
            ),
        ),
        migrations.AlterField(
            model_name="voyagelegprogress",
            name="latest_noon",
            field=models.OneToOneField(
                limit_choices_to={"report_type": "NOON"},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="vesselreporting.reportheader",
            ),
        ),
    ]
