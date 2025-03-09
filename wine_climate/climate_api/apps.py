import sys
import os
import threading
import time
from django.apps import AppConfig
from django.utils.timezone import now

def run_periodically(interval):  # Interval in seconds (86400s = 1 day)
    def task():
        from climate_api.services import update_climate_data_for_all_regions, calculate_climate_insights_for_all_regions
        from climate_api.models import ClimateInsights
        while True:
            print(f"Fetching latest metrics at {now()}")
            update_data_response = update_climate_data_for_all_regions()
            print(f"Fetching latest metrics response: {update_data_response}")

            if update_data_response["num_days_fetched"] > 0 or not ClimateInsights.objects.exists():
                print("Calculating climate insights...")
                insights_response = calculate_climate_insights_for_all_regions()
                print(f"Climate insights calculation response: {insights_response}")

            time.sleep(interval)

    thread = threading.Thread(target=task, daemon=True)
    thread.start()

class ClimateApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "climate_api"

    def ready(self):
        # Start the background task only if this is the main Django process
        if not any(arg in ["makemigrations", "migrate", "shell", "test"] for arg in sys.argv):
            run_periodically(86400)
