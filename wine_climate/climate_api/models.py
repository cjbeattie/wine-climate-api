from django.db import models

class WineRegion(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)  # Store latitude as a decimal
    longitude = models.DecimalField(max_digits=9, decimal_places=6)  # Store longitude as a decimal

    def __str__(self):
        return self.name