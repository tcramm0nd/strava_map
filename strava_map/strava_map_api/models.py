# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

# import polyline
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver 

class Activity(models.Model):
    class ActivityType(models.TextChoices):
        RUN = "1", "run"
        BIKE = "2", "bike"
    name = models.CharField()
    strava_id = models.BigIntegerField()
    # full_date_time = models.DateTimeField()
    date = models. DateField()
    time = models.TimeField()
    type = models.CharField(choices=ActivityType.choices)
    distance = models.FloatField()
    effort = models.IntegerField()

    # map = models.CharField()

    path = models.LineStringField(null=True)

    ###

    # @property
    # def generate_path(self) -> str:
    #     if self.map:
    #         decoded_polyline = polyline.decode(self.map)
    #         # return decoded_polyline
    #     else:
    #         return "LINESTRING()"

    #     points = ", ".join([f"{p[0]} {p[1]}" for p in decoded_polyline])
    #     line_string = f"LINESTRING({points})"
    #     return line_string

    # def save(self, *args, **kwargs):
    #     self.path = self.generate_path
    #     super().save(*args, **kwargs)


class ActivityPoints(models.Model):
    activity_id = models.ForeignKey(Activity, on_delete=models.CASCADE)
    point = models.PointField()


class RegionOfInterest(models.Model):
    name = models.CharField()
    area = models.PolygonField()


class Way(models.Model):
    name = models.CharField(null=True)
    explored = models.BooleanField(default=False)
    roi = models.ForeignKey(
        RegionOfInterest, on_delete=models.CASCADE, related_name='ways')
    path = models.LineStringField()



@receiver(post_save, sender=Activity)
def create_activity_points(sender,instance,**kwargs):
    pass