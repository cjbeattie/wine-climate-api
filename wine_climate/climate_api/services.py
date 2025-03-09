import requests
from datetime import datetime, timedelta
from climate_api.models import WineRegion, ClimateMetrics, ClimateInsights
from django.db.models import Max, Sum
from django.db import transaction
from django.db.models import Count
from django.db.models.functions import ExtractMonth

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


from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth

def calculate_percentage_of_days_in_ideal_temp_range_by_month_for_region(region_id, start_date=None, end_date=None):
    try:
        temp_min = 25
        temp_max = 32

        # Base queryset with optional date filtering
        base_queryset = ClimateMetrics.objects.filter(wine_region_id=region_id)
        if start_date and end_date:
            base_queryset = base_queryset.filter(date__range=[start_date, end_date])

        # Query to get the number of days in range for each month
        days_in_range_query = (
            base_queryset
            .filter(temperature_mean__gte=temp_min, temperature_mean__lte=temp_max)
            .annotate(month=ExtractMonth('date'))
            .values('month')
            .annotate(days_in_range=Count('id'))
            .order_by('month')
        )

        # Query to get the total number of days for each month
        total_days_query = (
            base_queryset
            .annotate(month=ExtractMonth('date'))
            .values('month')
            .annotate(total_days=Count('id'))
            .order_by('month')
        )

        # Convert to dictionaries for easier lookup
        days_in_range_dict = {item['month']: item['days_in_range'] for item in days_in_range_query}
        total_days_dict = {item['month']: item['total_days'] for item in total_days_query}

        # Create a result for all months (1-12)
        result = []
        for month in range(1, 13):
            days_in_range = days_in_range_dict.get(month, 0)
            total_days = total_days_dict.get(month, 0)
            percentage = (days_in_range / total_days) * 100 if total_days else 0

            result.append({
                'month': month,
                'days_in_range': days_in_range,
                'total_days': total_days,
                'percentage_in_range': percentage
            })

        return result

    except Exception as e:
        return f'Error calculating temperatures for region id {region_id}: {e}'


def calculate_percentage_of_days_in_ideal_humidity_range_by_month_for_region(region_id, start_date=None, end_date=None):
    try:
        humidity_min = 40
        humidity_max = 70

        # Base queryset with optional date filtering
        base_queryset = ClimateMetrics.objects.filter(wine_region_id=region_id)
        if start_date and end_date:
            base_queryset = base_queryset.filter(date__range=[start_date, end_date])

        # Query to get the number of days in range for each month
        days_in_range_query = (
            base_queryset
            .filter(relative_humidity_mean__gte=humidity_min, relative_humidity_mean__lte=humidity_max)
            .annotate(month=ExtractMonth('date'))
            .values('month')
            .annotate(days_in_range=Count('id'))
            .order_by('month')
        )

        # Query to get the total number of days for each month
        total_days_query = (
            base_queryset
            .annotate(month=ExtractMonth('date'))
            .values('month')
            .annotate(total_days=Count('id'))
            .order_by('month')
        )

        # Convert to dictionaries for easier lookup
        days_in_range_dict = {item['month']: item['days_in_range'] for item in days_in_range_query}
        total_days_dict = {item['month']: item['total_days'] for item in total_days_query}

        # Create a result for all months (1-12)
        result = []
        for month in range(1, 13):
            days_in_range = days_in_range_dict.get(month, 0)
            total_days = total_days_dict.get(month, 0)
            percentage = (days_in_range / total_days) * 100 if total_days else 0

            result.append({
                'month': month,
                'days_in_range': days_in_range,
                'total_days': total_days,
                'percentage_in_range': percentage
            })

        return result

    except Exception as e:
        return f'Error calculating humidity for region id {region_id}: {e}'


def calculate_total_precipitation_for_winter_for_region(region_id, start_date=None, end_date=None):
    try:
        winter_months = [6, 7, 8]  # June, July, August

        # Base queryset with optional date filtering
        base_queryset = ClimateMetrics.objects.filter(wine_region_id=region_id, date__month__in=winter_months)
        if start_date and end_date:
            base_queryset = base_queryset.filter(date__range=[start_date, end_date])

        # Aggregate total precipitation
        total_precipitation = base_queryset.aggregate(total_rainfall=Sum('precipitation_sum'))['total_rainfall'] or 0

        return total_precipitation

    except Exception as e:
        return f'Error calculating total precipitation for region id {region_id}: {e}'


def calculate_percentage_of_days_in_ideal_humidity_and_temperature_range_for_region(region_id, start_date=None, end_date=None):
    try:
        temp_min = 25
        temp_max = 32
        humidity_min = 40
        humidity_max = 70

        # Base queryset with optional date filtering
        base_queryset = ClimateMetrics.objects.filter(wine_region_id=region_id)
        if start_date and end_date:
            base_queryset = base_queryset.filter(date__range=[start_date, end_date])

        # Query to get the number of days where both temperature and humidity are in the ideal range
        valid_days_query = (
            base_queryset
            .filter(temperature_mean__gte=temp_min, temperature_mean__lte=temp_max)
            .filter(relative_humidity_mean__gte=humidity_min, relative_humidity_mean__lte=humidity_max)
            .annotate(month=ExtractMonth('date'))
            .values('month')
            .annotate(valid_days=Count('id'))  # Count only days where both conditions are met
            .order_by('month')
        )

        # Query to get the total number of days for the given date range
        total_days_query = (
            base_queryset
            .annotate(month=ExtractMonth('date'))
            .values('month')
            .annotate(total_days=Count('id'))
            .order_by('month')
        )

        # Convert to dictionaries for easier lookup
        valid_days_dict = {item['month']: item['valid_days'] for item in valid_days_query}
        total_days_dict = {item['month']: item['total_days'] for item in total_days_query}

        # Sum of all valid days and total days over the entire period
        total_valid_days = sum(valid_days_dict.values())
        total_total_days = sum(total_days_dict.values())

        # Calculate the percentage of days in the ideal range
        percentage = (total_valid_days / total_total_days) * 100 if total_total_days else 0

        # return percentage
        return round(percentage, 2)  # Round the percentage to two decimal places

    except Exception as e:
        return f'Error calculating ideal humidity and temperature range for region id {region_id}: {e}'



def calculate_climate_insights_for_region(region_id):
    pass
    # insights = {
    #     "count": 1,
    #     "items": [
    #         {
    #         "id": 1,
    #         "name": "McLaren Vale, South Australia",
    #         "optimal_time_of_year": {
    #             "start_month": 2,
    #             "end_month": 6
    #         },
    #         "performance_score_last_10_years": 0.6,
    #         "optimal_conditions_percentage_last_30_years": 60
    #         }
    #     ]
    # }

    # 1. "temperatures between 25 and 32 degrees Celsius" --> Calculate what percentage of each month has this temperature. Calculate percentage of summer months that has this temperature.
    # 2. "balanced humidity and what months they are" --> Internet says 40%-70% is optimal humidity for grape growth. Calculate what percentage of each month is within this humidity range.
    # 3. "long warm summers" --> covered in 1.
    # 4. adequately rainy winters - calculate total rainfall for Jun - Aug

    # optimal_time_of_year:  Seasonal Suitability: For each region, when is the best time of the year to grow grapes for wine production? --> (combo of points 1 and 2)
    # performance_score_last_10_years: Historical Performance: Over the past 10 years, which region has historically experienced the worst climate conditions for grape cultivation? identify trends in adverse conditions over the past decade. --> 
    # optimal_conditions_percentage_last_30_years: Long-term Viability: For each region, over a 30-year period, what percentage of that period can be expected to offer optimal conditions for grape production? determine the percentage of favorable years over a 30-year period
    
    try:
        # Set what the the threshold is for percentage of days in ideal temp/humidity range to be considered "optimal" - totally arbitrarily picked right now and would be a business decision normally
        ideal_temp_percentage_threshold = 15
        ideal_humidity_percentage_threshold = 30



        # OPTIMAL TIME OF YEAR

        # Get metrics for all records in the database (i.e. no date limit)
        temp_result_all_time = calculate_percentage_of_days_in_ideal_temp_range_by_month_for_region(region_id)
        humidity_result_all_time = calculate_percentage_of_days_in_ideal_humidity_range_by_month_for_region(region_id)

        optimal_time_of_year_temperature_all_time = [x for x in temp_result_all_time if x["percentage_in_range"] > ideal_temp_percentage_threshold]
        optimal_time_of_year_humidity_all_time = [x for x in humidity_result_all_time if x["percentage_in_range"] > ideal_humidity_percentage_threshold]
        optimal_time_of_year_month_arr_all_time = []

        # Extract out the months where both temperature and humidity pass the threshold for being "optimal"
        for i in optimal_time_of_year_temperature_all_time:
            for j in optimal_time_of_year_humidity_all_time:
                if j["month"] == i["month"]:
                    optimal_time_of_year_month_arr_all_time.append(j["month"])

        optimal_time_of_year_month_arr_all_time.sort()

        # Will assume that the optimal time of year may contain months that aren't optimal, i.e. optimal months don't have to be contiguous

        if optimal_time_of_year_month_arr_all_time:
            optimal_time_of_year_start_month = optimal_time_of_year_month_arr_all_time[0]
            optimal_time_of_year_end_month = optimal_time_of_year_month_arr_all_time[-1]
        else:
            # Handle the case where no months pass the threshold
            optimal_time_of_year_start_month = None
            optimal_time_of_year_end_month = None




        # PERFORMANCE LAST 10 YEARS

        # Get start and end dates for last 10 years
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=365 * 10)

        # calculate total winter PRECIPITATION for this region in the last 10 years 
        past_10_years_winter_precipitation_total = calculate_total_precipitation_for_winter_for_region(region_id, start_date=start_date, end_date=end_date)

        # calculate percentage of days in optimal TEMPERATURE range for this region in last 10 years
        temp_result_last_10_yrs = calculate_percentage_of_days_in_ideal_temp_range_by_month_for_region(region_id, start_date=start_date, end_date=end_date)
        total_days_in_temp_range_over_10_years = sum(item['days_in_range'] for item in temp_result_last_10_yrs)
        total_days_in_10_years_temp = sum(item['total_days'] for item in temp_result_last_10_yrs)

        if total_days_in_10_years_temp > 0:
            past_10_years_percentage_days_in_optimal_temp_range = (total_days_in_temp_range_over_10_years / total_days_in_10_years_temp) * 100
        else:
            past_10_years_percentage_days_in_optimal_temp_range = 0

        # calculate percentage of days in optimal HUMIDITY range for this region in last 10 years
        humidity_result_last_10_yrs = calculate_percentage_of_days_in_ideal_humidity_range_by_month_for_region(region_id, start_date=start_date, end_date=end_date)
        total_days_in_humidity_range_over_10_years = sum(item['days_in_range'] for item in humidity_result_last_10_yrs)
        total_days_in_10_years_humidity = sum(item['total_days'] for item in humidity_result_last_10_yrs)

        if total_days_in_10_years_humidity > 0:
            past_10_years_percentage_days_in_optimal_humidity_range = (total_days_in_humidity_range_over_10_years / total_days_in_10_years_humidity) * 100
        else:
            past_10_years_percentage_days_in_optimal_humidity_range = 0




        # OPTIMAL CONDITIONS PERCENTAGE LAST 30 YEARS
            
        # Get start and end dates for last 30 years
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=365 * 30)

        past_30_years_percentage_of_days_in_ideal_humidity_and_temperature_range = calculate_percentage_of_days_in_ideal_humidity_and_temperature_range_for_region(region_id, start_date=start_date, end_date=end_date)
        
            
        result = {
            "region_id": region_id,
            "optimal_time_of_year_start_month": optimal_time_of_year_start_month,
            "optimal_time_of_year_end_month": optimal_time_of_year_end_month,
            "past_10_years_winter_precipitation_total": past_10_years_winter_precipitation_total,
            "past_10_years_percentage_days_in_optimal_temp_range": past_10_years_percentage_days_in_optimal_temp_range,
            "past_10_years_percentage_days_in_optimal_humidity_range": past_10_years_percentage_days_in_optimal_humidity_range,
            "past_30_years_percentage_of_days_in_ideal_humidity_and_temperature_range": past_30_years_percentage_of_days_in_ideal_humidity_and_temperature_range,
        }

        return result
    
    except Exception as e:
        return (f'Error calculating climate insights for region id {region_id}: {e}')





def calculate_climate_insights_for_all_regions():
    try:
        regions = WineRegion.objects.all()

        with transaction.atomic(): 
            for region in regions:
                insights = calculate_climate_insights_for_region(region.id)
                ClimateInsights.objects.create(
                    wine_region = region,
                    optimal_time_of_year_start_month = insights["optimal_time_of_year_start_month"],
                    optimal_time_of_year_end_month = insights["optimal_time_of_year_end_month"],
                    past_10_years_winter_precipitation_total = insights["past_10_years_winter_precipitation_total"],
                    past_10_years_percentage_days_in_optimal_temp_range = insights["past_10_years_percentage_days_in_optimal_temp_range"],
                    past_10_years_percentage_days_in_optimal_humidity_range = insights["past_10_years_percentage_days_in_optimal_humidity_range"],
                    optimal_conditions_percentage_last_30_years = insights["past_30_years_percentage_of_days_in_ideal_humidity_and_temperature_range"]

                )

        print("Calculated climate insights for all regions")

    except Exception as e:
        return (f'Error calculating climate insights for all regions: {str(e)}')