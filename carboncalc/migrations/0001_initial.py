# Generated by Django 4.1.1 on 2023-03-01 18:24

import django.contrib.postgres.fields
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TargetCII",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("year", models.PositiveSmallIntegerField()),
                (
                    "grade",
                    models.TextField(
                        choices=[
                            ("A", "CII Grade A"),
                            ("B", "CII Grade A"),
                            ("C", "CII Grade A"),
                            ("D", "CII Grade A"),
                            ("E", "CII Grade A"),
                        ],
                        max_length=1,
                    ),
                ),
                (
                    "ship",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="core.ship"
                    ),
                ),
            ],
            options={
                "db_table": "target_ciis",
            },
        ),
        migrations.CreateModel(
            name="StandardizedDataReportingFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("file_name", models.CharField(max_length=127)),
                ("s3_file_path", models.CharField(max_length=255)),
                ("deleted", models.BooleanField(default=False)),
                ("year", models.PositiveSmallIntegerField()),
                (
                    "acceptance_status",
                    models.CharField(
                        choices=[
                            ("ACCEPTED", "Accepted"),
                            ("PROCESSING", "Processing"),
                            ("ERROR", "Error"),
                        ],
                        default="PROCESSING",
                        max_length=15,
                    ),
                ),
                ("error_message", models.TextField(blank=True, null=True)),
                (
                    "ship",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="core.ship"
                    ),
                ),
            ],
            options={
                "db_table": "standardized_data_reporting_file",
            },
        ),
        migrations.CreateModel(
            name="StandardizedDataReportingData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("year", models.PositiveSmallIntegerField()),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("gross_tonnage", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "deadweight_tonnage",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("total_hours", models.DecimalField(decimal_places=3, max_digits=7)),
                ("total_distance", models.DecimalField(decimal_places=2, max_digits=8)),
                (
                    "fuel_oil_burned",
                    models.JSONField(
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                (
                    "reporting_file",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="carboncalc.standardizeddatareportingfile",
                    ),
                ),
                (
                    "ship",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="core.ship"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="EnergyEfficiencyTechnicalFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("file_name", models.CharField(max_length=127)),
                ("s3_file_path", models.CharField(max_length=255)),
                ("deleted", models.BooleanField(default=False)),
                (
                    "energy_efficiency_index_type",
                    models.CharField(
                        choices=[("EEXI", "EEXI"), ("EEDI", "EEDI")], max_length=4
                    ),
                ),
                (
                    "ship",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="core.ship"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CIIShipYearBoundaries",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("year", models.PositiveSmallIntegerField()),
                ("boundary_a", models.DecimalField(decimal_places=3, max_digits=6)),
                ("boundary_b", models.DecimalField(decimal_places=3, max_digits=6)),
                ("boundary_c", models.DecimalField(decimal_places=3, max_digits=6)),
                ("boundary_d", models.DecimalField(decimal_places=3, max_digits=6)),
                (
                    "ship",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="core.ship"
                    ),
                ),
            ],
            options={
                "db_table": "cii_ship_year_boundaries",
            },
        ),
        migrations.CreateModel(
            name="CIIRawData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("year", models.PositiveSmallIntegerField()),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("distance_sailed", models.PositiveIntegerField()),
                (
                    "fuel_oil_burned",
                    models.JSONField(
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                (
                    "ship",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="core.ship"
                    ),
                ),
            ],
            options={
                "db_table": "cii_raw_data",
            },
        ),
        migrations.CreateModel(
            name="CIIConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "energy_efficiency_index_type",
                    models.CharField(
                        choices=[("EEXI", "EEXI"), ("EEDI", "EEDI")], max_length=4
                    ),
                ),
                (
                    "energy_efficiency_index_value",
                    models.DecimalField(decimal_places=3, max_digits=6),
                ),
                ("is_engine_power_limited", models.BooleanField()),
                (
                    "engine_power_limit_type",
                    models.CharField(
                        blank=True,
                        choices=[("EPL", "EPL"), ("SPL", "Shapoli")],
                        max_length=4,
                        null=True,
                    ),
                ),
                (
                    "engine_power_limit_value",
                    models.IntegerField(blank=True, null=True),
                ),
                ("imo_dcs", models.BooleanField(default=True)),
                (
                    "imo_dcs_method",
                    models.TextField(
                        choices=[
                            ("DCS1", "DCS Method 1"),
                            ("DCS2", "DCS Method 2"),
                            ("DCS3", "DCS Method 3"),
                        ],
                        max_length=4,
                    ),
                ),
                ("eu_mrv", models.BooleanField(default=False)),
                (
                    "eu_mrv_method",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("MRVA", "MRV Method A"),
                            ("MRVB", "MRV Method B"),
                            ("MRVC", "MRV Method C"),
                            ("MRVD", "MRV Method D"),
                        ],
                        max_length=4,
                        null=True,
                    ),
                ),
                (
                    "applicable_cii",
                    models.CharField(
                        choices=[("AER", "AER"), ("CGDIST", "cgDIST")], max_length=8
                    ),
                ),
                (
                    "trial_cii_types",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("EEPI", "EEPI"),
                                ("CBDIST", "cbDIST"),
                                ("CLDIST", "clDIST"),
                                ("EEOI", "EEOI"),
                            ],
                            max_length=8,
                        ),
                        default=list,
                        size=None,
                    ),
                ),
                (
                    "fuel_options",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("HFO", "HFO"),
                                ("LSFO", "LSFO"),
                                ("MDGO", "MDO/MGO"),
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
                (
                    "ship",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT, to="core.ship"
                    ),
                ),
            ],
            options={
                "db_table": "cii_configs",
            },
        ),
        migrations.CreateModel(
            name="CalculatedCII",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("year", models.PositiveSmallIntegerField()),
                ("value", models.DecimalField(decimal_places=3, max_digits=6)),
                (
                    "grade",
                    models.TextField(
                        choices=[
                            ("A", "CII Grade A"),
                            ("B", "CII Grade A"),
                            ("C", "CII Grade A"),
                            ("D", "CII Grade A"),
                            ("E", "CII Grade A"),
                        ],
                        max_length=1,
                    ),
                ),
                (
                    "ship",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="core.ship"
                    ),
                ),
            ],
            options={
                "db_table": "calculated_ciis",
            },
        ),
        migrations.AddConstraint(
            model_name="targetcii",
            constraint=models.UniqueConstraint(
                fields=("ship", "year"), name="targetcii_ship_year"
            ),
        ),
        migrations.AddConstraint(
            model_name="standardizeddatareportingfile",
            constraint=models.UniqueConstraint(
                fields=("ship", "year"), name="standardizeddatareportingfile_ship_year"
            ),
        ),
        migrations.AddConstraint(
            model_name="ciishipyearboundaries",
            constraint=models.UniqueConstraint(
                fields=("ship", "year"), name="ciishipyearboundaries_ship_year"
            ),
        ),
        migrations.AddConstraint(
            model_name="ciirawdata",
            constraint=models.UniqueConstraint(
                fields=("ship", "year"), name="ciirawdata_ship_year"
            ),
        ),
        migrations.AddConstraint(
            model_name="calculatedcii",
            constraint=models.UniqueConstraint(
                fields=("ship", "year"), name="calculatedcii_ship_year"
            ),
        ),
    ]
