# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from rest_framework import serializers
from .models import Activity

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('__all__')
        # exclude = ('map')
