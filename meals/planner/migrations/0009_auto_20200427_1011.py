# Generated by Django 3.0.3 on 2020-04-27 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0008_recipe_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='url',
            field=models.URLField(max_length=255),
        ),
    ]
