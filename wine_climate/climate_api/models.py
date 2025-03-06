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
    date = models.DateField()
    temperature_mean = models.FloatField(max_digits=5, decimal_places=1)
    relative_humidity_mean = models.IntegerField(
        null=True, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    precipitation_sum = models.FloatField(max_digits=6, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=['wine_region', 'date']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['wine_region', 'date'], name='unique_wine_region_date')
        ]


class ClimateInsights(models.Model):
    wine_region = models.ForeignKey(WineRegion, on_delete=models.CASCADE, db_index=True)
    optimal_time_of_year_start_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    optimal_time_of_year_end_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    performance_score_last_10_years = models.DecimalField(
        max_digits=3, decimal_places=2, validators=[MinValueValidator(0.00), MaxValueValidator(1.00)]
    )
    optimal_conditions_percentage_last_30_years = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['wine_region']),
            models.Index(fields=['created_at'])
        ]