from rest_framework import serializers
from .models import WineRegion

class WineRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WineRegion
        fields = (
            'id',
            'name',
            'latitude',
            'longitude'
        )