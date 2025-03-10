from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class WineRegion(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.name

class ClimateMetrics(models.Model):
    wine_region = models.ForeignKey(WineRegion, on_delete=models.CASCADE, db_index=True)
    metric_date = models.DateField()
    temperature_mean = models.DecimalField(max_digits=5, decimal_places=1)
    relative_humidity_mean = models.IntegerField(
        null=True, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    precipitation_sum = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=['wine_region', 'metric_date']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['wine_region', 'metric_date'], name='unique_wine_region_metric_date')
        ]

class ClimateInsights(models.Model):
    wine_region = models.ForeignKey(WineRegion, on_delete=models.CASCADE, db_index=True)
    optimal_time_of_year_start_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)], null=True, blank=True
    )
    optimal_time_of_year_end_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)], null=True, blank=True
    )
    past_10_years_winter_precipitation_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    past_10_years_percentage_days_in_optimal_temp_range = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00), MaxValueValidator(1.00)], default=0.00
    )
    past_10_years_percentage_days_in_optimal_humidity_range = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00), MaxValueValidator(1.00)], default=0.00
    )
    optimal_conditions_percentage_last_30_years = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00), MaxValueValidator(1.00)], default=0.00
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['wine_region']),
            models.Index(fields=['created_at'])
        ]