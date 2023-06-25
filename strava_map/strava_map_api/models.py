# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from typing import List

import polyline
from django.contrib.gis.db import models


class Activity(models.Model):
    class ActivityType(models.TextChoices):
        RUN = "1", "run"
        BIKE = "2", "bike"
    name = models.CharField()
    date_time = models.DateTimeField()
    date = models. DateField()
    time = models.TimeField()
    type = models.CharField(choices=ActivityType.choices)
    distance = models.FloatField()

    map = models.CharField()

    path = models.LineStringField()

    ###

    @property
    def generate_path(self) -> List:
        """Converts Encoded Polyline to coordinates

        Args:
            map_data (dict): Dictionary of Activity Data.

        Returns:
            list: Decoded polyline as coordinates list.
        """

        # encoded_polyline = self.map['summary_polyline']

        if self.map:
            decoded_polyline = polyline.decode(self.map)
            return decoded_polyline
        else:
            return []

    def save(self, *args, **kwargs):
        self.path = self.generate_path
        super().save(*args, **kwargs)


class ActivityPoints(models.Model):
    activity_id = models.ForeignKey(Activity, on_delete=models.CASCADE)
    point = models.PointField()


class RegionOfInterest(models.Model):
    name = models.CharField()
    area = models.PolygonField()


class Way(models.Model):
    name = models.CharField(null=True)
    explored = models.BooleanField(default=False)
    roi = models.ForeignKey(RegionOfInterest, on_delete=models.CASCADE)
    path = models.LineStringField()
