# Generated by Django 3.0.3 on 2020-04-26 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0006_report'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('ingredients', models.CharField(max_length=2500)),
                ('steps', models.CharField(max_length=5000)),
                ('img', models.URLField(max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='report',
            name='img',
        ),
        migrations.RemoveField(
            model_name='report',
            name='ingredients',
        ),
        migrations.RemoveField(
            model_name='report',
            name='steps',
        ),
        migrations.RemoveField(
            model_name='report',
            name='title',
        ),
        migrations.AddField(
            model_name='report',
            name='recipes',
            field=models.ManyToManyField(related_name='recipes_by_report', to='planner.Recipe'),
        ),
    ]