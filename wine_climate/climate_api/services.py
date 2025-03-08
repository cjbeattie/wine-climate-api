import requests
from datetime import datetime, timedelta
from climate_api.models import WineRegion, ClimateMetrics
from django.db.models import Max
from django.db import transaction

def fetch_climate_data_for_region(latitude, longitude, start_date, end_date):

    url = f"https://climate-api.open-meteo.com/v1/climate?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&models=CMCC_CM2_VHR4&daily=temperature_2m_mean,relative_humidity_2m_mean,precipitation_sum"

    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an error for 4xx or 5xx responses
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching climate data: {e}")
        return None
    

def update_climate_data_for_all_regions():
    try:
        # Check db to see which dates we have records for. Get whatever is missing in the last 30 years from today.

        # Firstly, figure out start_date and end_date
        last_record = ClimateMetrics.objects.filter().aggregate(Max('date'))
        last_fetched_date = last_record['date__max']

        if not last_fetched_date:
            start_date = datetime.now() - timedelta(days=30*365)  # 30 years ago
        else:
            if last_fetched_date == datetime.now().date():
                # we're up to date already
                return {
                    'success': True,
                    'num_days_fetched': 0,
                    'error': None
                }
            else:
                start_date = last_fetched_date + timedelta(days=1)
            
        end_date = datetime.now()

        # Ensure they're dates (not datetimes) to avoid weird errors
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()

        print(f"Start date is {start_date}")
        print(f"End date is {end_date}")            

        if start_date > end_date:
            raise ValueError("Start date is later than end date.")
        
        num_days = (end_date - start_date).days

        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # Get data for those dates for all wine regions. Roll back if anything fails.
        wine_regions = WineRegion.objects.all()

        with transaction.atomic(): 
            for region in wine_regions:
                climate_data = fetch_climate_data_for_region(region.latitude, region.longitude, start_date_str, end_date_str)

                if climate_data:
                    dates = climate_data.get('daily', {}).get('time', [])
                    temperature = climate_data.get('daily', {}).get('temperature_2m_mean', [])
                    humidity = climate_data.get('daily', {}).get('relative_humidity_2m_mean', [])
                    precipitation = climate_data.get('daily', {}).get('precipitation_sum', [])

                    # Ensure all lists have the same length (they should, but just in case)
                    if len(dates) == len(temperature) == len(humidity) == len(precipitation):
                        existing_dates = set(ClimateMetrics.objects.filter(wine_region=region).values_list('date', flat=True))
                        for i in range(len(dates)):
                            if dates[i] not in existing_dates:
                                ClimateMetrics.objects.create(
                                    wine_region=region,
                                    date=dates[i],
                                    temperature_mean=temperature[i],
                                    relative_humidity_mean=humidity[i],
                                    precipitation_sum=precipitation[i]
                                )
                        print(f"Added climate data for {region.name}")
                    else:
                        raise Exception(f"Data length mismatch for {region.name}.")
                else:
                    raise Exception(f"Failed to fetch or save data for {region.name}")

        return {
            'success': True,
            'num_days_fetched': num_days,
            'error': None
        }

    except Exception as e:
        return {
            'success': False,
            'records_added': 0,
            'error': str(e)
        }


def calculate_climate_insights():
    # # Fetch climate data for the region
    # climate_data = ClimateMetrics.objects.filter(wine_region=region)
    
    # if not climate_data.exists():
    #     return None
    
    # # Perform calculations (example: average temperature)
    # avg_temp = climate_data.aggregate(Avg('temperature_mean'))['temperature_mean__avg']
    
    # # Save insights
    # insights, created = ClimateInsights.objects.update_or_create(
    #     wine_region=region,
    #     defaults={'average_temperature': avg_temp}
    # )

    insights = {
        "count": 1,
        "items": [
            {
            "id": 1,
            "name": "McLaren Vale, South Australia",
            "optimal_time_of_year": {
                "start_month": 2,
                "end_month": 6
            },
            "performance_score_last_10_years": 0.6,
            "optimal_conditions_percentage_last_30_years": 60
            }
        ]
    }
    
    return insights