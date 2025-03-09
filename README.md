# Wine Climate API
An API that analyzes climate data to determine the best regions for growing wine grapes.

## Design Approach
I have created a simple endpoint that provides insights into the optimal growing conditions for wine in each of the provided wine regions. The user can optionally provide a region ID to retrieve insights for a single region.

I felt it important for performance reasons to do the following:
- Since data from Open Meteo Climate API is by day, set an offline task to retrieve new metrics once a day and store in a table called `climate_metrics`.
- Only retrive climate metrics for days that haven't been fetched yet in the last 30 years. Initial fetch will be quite large and will retrieve records for the last 30 years, but subsequent calls should only be one day's worth of data to fetch.
- Once those metrics have been fetched, run the algorithms that calculate the insights and store the results in a separate table called `climate_insights`. Insights SHOULD NOT be calculated when the user hits the endpoint. There's no point - metrics data is only updated once per day, so there's no need to recaluclate on every request.
- Any time the user makes a request to the climate-insights endpoint, simply fetch the pre-calculated data from the `climate_insights` table.
- A table that references all the listed `wine_regions` also exists to link all data via foreign key to the respective wine region.
- Any aggregation functions are done at the database using Django's ORM rather than calculated in python code. This avoids unnecessary amounts of data being loaded into memory.


### Database Schema
![My Image](images/DBSchema.png)

### Addressing Requirements - ******************WIP
Several assumptions were made which would normally be business decisions, and the appropriate channels consulted. However for the sake of this test I have made the following decisions:
- When calculating 



1. "temperatures between 25 and 32 degrees Celsius" --> Calculate what percentage of each month has this temperature. Calculate percentage of summer months that has this temperature.
2. "balanced humidity and what months they are" --> Internet says 40%-70% is optimal humidity for grape growth. Calculate what percentage of each month is within this humidity range.
3. "long warm summers" --> covered in 1.
4. adequately rainy winters - calculate total rainfall for Jun - Aug

optimal_time_of_year:  Seasonal Suitability: For each region, when is the best time of the year to grow grapes for wine production? --> (combo of points 1 and 2)
performance_score_last_10_years: Historical Performance: Over the past 10 years, which region has historically experienced the worst climate conditions for grape cultivation? identify trends in adverse conditions over the past decade. --> 
optimal_conditions_percentage_last_30_years: Long-term Viability: For each region, over a 30-year period, what percentage of that period can be expected to offer optimal conditions for grape production? determine the percentage of favorable years over a 30-year period

- Calculating optimal time of year is based on on ALL records in db, so a more accurate result may be calculated by having more history in the db
- using ORM for aggregation of metrics, not loading heaps of data in memory
- Not wanting to take an average per month, rather a percentage of days in range. Average not as useful as it discards the extremes.
- for caluclating the "optimal conditions percentage over last 30 years" I'll discard the rainfall measurement as "adequate rainy winters" isn't clearly defined






## API Documentation
This API provides insights into climate conditions for wine regions based on historical climate data.

### Base URL
`http://127.0.0.1:8000/api/`

### Endpoints

**1. Get All Climate Insights**  
Endpoint: `GET /climate-insights/`  
Description: Retrieves climate insights for all wine regions.  
Response Example:  

<details>
    <summary>CLICK TO EXPAND</summary>

```json
[
    {
        "wine_region": {
            "id": 1,
            "name": "McLaren Vale, South Australia"
        },
        "optimal_time_of_year": {
            "start_month": 1,
            "end_month": 2
        },
        "performance_past_10_years": {
            "winter_precipitation_total": "2350.35",
            "percentage_days_in_optimal_temp_range": "5.07",
            "percentage_days_in_optimal_humidity_range": "39.47"
        },
        "optimal_conditions_percentage_last_30_years": "2.84"
    },
    {
        "wine_region": {
            "id": 2,
            "name": "Margaret River, Western Australia"
        },
        "optimal_time_of_year": {
            "start_month": null,
            "end_month": null
        },
        "performance_past_10_years": {
            "winter_precipitation_total": "3466.09",
            "percentage_days_in_optimal_temp_range": "3.07",
            "percentage_days_in_optimal_humidity_range": "49.16"
        },
        "optimal_conditions_percentage_last_30_years": "1.66"
    },
    {
        "wine_region": {
            "id": 3,
            "name": "Mornington, Victoria"
        },
        "optimal_time_of_year": {
            "start_month": 2,
            "end_month": 2
        },
        "performance_past_10_years": {
            "winter_precipitation_total": "2166.83",
            "percentage_days_in_optimal_temp_range": "4.11",
            "percentage_days_in_optimal_humidity_range": "37.93"
        },
        "optimal_conditions_percentage_last_30_years": "2.42"
    },
    {
        "wine_region": {
            "id": 4,
            "name": "Coonawarra, South Australia"
        },
        "optimal_time_of_year": {
            "start_month": 1,
            "end_month": 2
        },
        "performance_past_10_years": {
            "winter_precipitation_total": "2125.36",
            "percentage_days_in_optimal_temp_range": "5.15",
            "percentage_days_in_optimal_humidity_range": "38.15"
        },
        "optimal_conditions_percentage_last_30_years": "2.26"
    },
    {
        "wine_region": {
            "id": 5,
            "name": "Yarra Valley, Victoria"
        },
        "optimal_time_of_year": {
            "start_month": 1,
            "end_month": 2
        },
        "performance_past_10_years": {
            "winter_precipitation_total": "1628.37",
            "percentage_days_in_optimal_temp_range": "4.33",
            "percentage_days_in_optimal_humidity_range": "32.76"
        },
        "optimal_conditions_percentage_last_30_years": "2.75"
    }
]
```
</details>
<br/>


**2. Get Climate Insights for a Specific Region**  
Endpoint: `GET /climate-insights/{region_id}`  
Description:  
Retrieves climate insights for a specific wine region. If no region_id is provided, all insights are returned.  
Path Parameters:  
| Parameter | Type | Required | Description |
| ----------- | ----------- | ------- | ------- |
| `region_id` | int | No | The ID of the wine region to filter by |

Response Example:  
<details>
    <summary>CLICK TO EXPAND</summary>

```json
{
    "wine_region": {
        "id": 4,
        "name": "Coonawarra, South Australia"
    },
    "optimal_time_of_year": {
        "start_month": 1,
        "end_month": 2
    },
    "performance_past_10_years": {
        "winter_precipitation_total": "2125.36",
        "percentage_days_in_optimal_temp_range": "5.15",
        "percentage_days_in_optimal_humidity_range": "38.15"
    },
    "optimal_conditions_percentage_last_30_years": "2.26"
}
```
</details>
<br/>





## Project Setup

To get started with this project, follow the steps below:

### Clone and install

1. Clone the repository:  
`git clone git@github.com:cjbeattie/wine-climate-api.git`  
`cd wine-climate-api`  

2. Make sure you have **Python 3** installed. You can check with:  
`python3 --version`  

3. Create and activate a virtual environment:  
`python3 -m venv env`  
`source env/bin/activate`  (On Windows use `env\Scripts\activate`)  
(to deactivate the virtual environment when you're done: `deactivate`)  

4. Install project dependencies:  
`pip install -r requirements.txt`  

If you have issues installing psocopg2, you may need to install postgreSQL development libraries that provide the pg_config tool:  
`brew install postgresql`  
`brew services start postgresql`  
(for Windows installation, go to https://www.postgresql.org/download/windows/)  

### Database Setup
1. Ensure you have PostgreSQL running locally:  
 `brew services start postgresql`  

2. Run the setup_db.sh script to set up the local database with the password I provide:  
`./setup_db.sh`  

3. Configure the database URL:  
-Create a `.env` file and add the `DATABASE_URL` I provide  

4. Navigate to `<your repo location>/wine-climate-api/wine_climate` and run:  
`python manage.py migrate`  

### Run the Server

1. Run the Django server:  
`python manage.py runserver`  

2. Open Postman or your favourite API testing tool and fetch database using GET `http://127.0.0.1:8000/api/climate-metrics/`  

## Known issues
- The periodic task fetches and analyzes the climate data twice per iteration due to the current implementation. This occurs because both the background thread and the main server process trigger the task when the Django server starts. In a real-world implementation, this would typically be handled using Celery, which would allow for more reliable and scalable task scheduling, prevent multiple triggers, and ensure that background tasks are properly managed outside the request/response cycle.