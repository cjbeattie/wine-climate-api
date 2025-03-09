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

class ClimateInsightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClimateInsights
        fields = "__all__"  # Keeps flexibility, but we override output below

    def to_representation(self, instance):
        data = super().to_representation(instance)

        return {
            "wine_region": {
                "id": data["wine_region"],
                "name": instance.wine_region.name,
            },
            "optimal_time_of_year": {
                "start_month": data["optimal_time_of_year_start_month"],
                "end_month": data["optimal_time_of_year_end_month"],
            },
            "performance_past_10_years": {
                "winter_precipitation_total": data["past_10_years_winter_precipitation_total"],
                "percentage_days_in_optimal_temp_range": data["past_10_years_percentage_days_in_optimal_temp_range"],
                "percentage_days_in_optimal_humidity_range": data["past_10_years_percentage_days_in_optimal_humidity_range"],
            },
            "optimal_conditions_percentage_last_30_years": data["optimal_conditions_percentage_last_30_years"],
        }