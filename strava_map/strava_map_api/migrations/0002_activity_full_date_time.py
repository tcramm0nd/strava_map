# Generated by Django 4.2.2 on 2023-06-25 03:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strava_map_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='full_date_time',
            field=models.DateTimeField(default='2018-05-02T12:15:09Z'),
            preserve_default=False,
        ),
    ]