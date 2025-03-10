# Generated by Django 4.2.19 on 2025-03-09 03:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climate_api', '0005_alter_climateinsights_optimal_time_of_year_end_month_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='climateinsights',
            name='optimal_conditions_percentage_last_30_years',
            field=models.DecimalField(decimal_places=20, default=0.0, max_digits=30, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)]),
        ),
    ]
