# Generated by Django 4.1.1 on 2023-01-15 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marinanet', '0014_bdndata_is_before_arrival'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voyagelegdata',
            name='freshwater_cons_in_harbour_port',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='voyagelegdata',
            name='freshwater_discharge_in_harbour_port',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='voyagelegdata',
            name='freshwater_gen_in_harbour_port',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='voyagelegdata',
            name='freshwater_receipt_in_harbour_port',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='voyagelegdata',
            name='freshwater_rob',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
