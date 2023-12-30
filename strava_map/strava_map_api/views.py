# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# from django.shortcuts import render
from rest_framework import viewsets
from .serializers import ActivitySerializer, ActivityPointsSerializer, RegionOfInterestSerializer, WaySerializer
from .models import Activity, ActivityPoints, RegionOfInterest, Way

# Create your views here.

# pylint: disable=no-member
class ActivityView(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    queryset = Activity.objects.all()


class ActivityPointsView(viewsets.ModelViewSet):
    serializer_class = ActivityPointsSerializer
    queryset = ActivityPoints.objects.all()


class RegionOfInterestView(viewsets.ModelViewSet):
    serializer_class = RegionOfInterestSerializer
    queryset = RegionOfInterest.objects.all()


class WayView(viewsets.ModelViewSet):
    serializer_class = WaySerializer
    queryset = Way.objects.all()
