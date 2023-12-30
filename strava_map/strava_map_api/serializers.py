# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from rest_framework import serializers
from .models import Activity, ActivityPoints, RegionOfInterest, Way

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('__all__')
        # exclude = ('map')
class ActivityPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityPoints
        fields = ('__all__')
class RegionOfInterestSerializer(serializers.ModelSerializer):
    # ways = serializers.CharField(source='category.name')

    class Meta:
        model = RegionOfInterest
        fields = ('__all__')
class WaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Way
        fields = ('__all__')