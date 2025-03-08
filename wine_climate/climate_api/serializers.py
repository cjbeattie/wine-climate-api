from rest_framework import serializers
from .models import WineRegion, ClimateInsights

class WineRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WineRegion
        fields = (
            'id',
            'name',
            'latitude',
            'longitude'
        )

class ClimateInsightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClimateInsights
        fields = (
            'wine_region',
            'optimal_time_of_year_start_month',
            'optimal_time_of_year_end_month',
            'performance_score_last_10_years',
            'optimal_conditions_percentage_last_30_years',
            'created_at'
        )