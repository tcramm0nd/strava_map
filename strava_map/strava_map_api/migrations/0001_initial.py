# Generated by Django 4.2.2 on 2023-06-25 03:12

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField()),
                ('date_time', models.DateTimeField()),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('type', models.CharField(choices=[('1', 'run'), ('2', 'bike')])),
                ('distance', models.FloatField()),
                ('map', models.CharField()),
                ('path', django.contrib.gis.db.models.fields.LineStringField(srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='RegionOfInterest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField()),
                ('area', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='Way',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(null=True)),
                ('explored', models.BooleanField(default=False)),
                ('path', django.contrib.gis.db.models.fields.LineStringField(srid=4326)),
                ('roi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strava_map_api.regionofinterest')),
            ],
        ),
        migrations.CreateModel(
            name='ActivityPoints',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('activity_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strava_map_api.activity')),
            ],
        ),
    ]
