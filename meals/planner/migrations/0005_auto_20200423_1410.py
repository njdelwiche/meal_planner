# Generated by Django 3.0.3 on 2020-04-23 18:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0004_auto_20200422_0911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='amount',
            field=models.IntegerField(default=10000, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
