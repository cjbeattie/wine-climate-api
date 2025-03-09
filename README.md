# wine-climate-api
An API that analyzes climate data to determine the best regions for growing wine grapes.

## Project Setup

To get started with this project, follow the steps below:

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

## Database Setup
1. Ensure you have PostgreSQL running locally:
 `brew services start postgresql`

2. Run the setup_db.sh script to set up the local database with the password I provide:
`./setup_db.sh`

3. Configure the database URL:
-Create a `.env` file and add the `DATABASE_URL` I provide

4. Navigate to `<your repo location>/wine-climate-api/wine_climate` and run:
`python manage.py migrate`

5. Run the Django server:
`python manage.py runserver`

6. Open Postman or your favourite API testing tool and fetch database using GET `http://127.0.0.1:8000/api/climate-metrics/`



## Design decisions

    # 1. "temperatures between 25 and 32 degrees Celsius" --> Calculate what percentage of each month has this temperature. Calculate percentage of summer months that has this temperature.
    # 2. "balanced humidity and what months they are" --> Internet says 40%-70% is optimal humidity for grape growth. Calculate what percentage of each month is within this humidity range.
    # 3. "long warm summers" --> covered in 1.
    # 4. adequately rainy winters - calculate total rainfall for Jun - Aug

    # optimal_time_of_year:  Seasonal Suitability: For each region, when is the best time of the year to grow grapes for wine production? --> (combo of points 1 and 2)
    # performance_score_last_10_years: Historical Performance: Over the past 10 years, which region has historically experienced the worst climate conditions for grape cultivation? identify trends in adverse conditions over the past decade. --> 
    # optimal_conditions_percentage_last_30_years: Long-term Viability: For each region, over a 30-year period, what percentage of that period can be expected to offer optimal conditions for grape production? determine the percentage of favorable years over a 30-year period

    
- Calculating optimal time of year is based on on ALL records in db, so a more accurate result may be calculated by having more history in the db
- using ORM for aggregation of metrics, not loading heaps of data in memory
- Not wanting to take an average per month, rather a percentage of days in range. Average not as useful as it discards the extremes.
- for caluclating the "optimal conditions percentage over last 30 years" I'll discard the rainfall measurement as "adequate rainy winters" isn't clearly defined

## Known issues
- The periodic task fetches and analyzes the climate data twice per iteration due to the current implementation. This occurs because both the background thread and the main server process trigger the task when the Django server starts. In a real-world implementation, this would typically be handled using Celery, which would allow for more reliable and scalable task scheduling, prevent multiple triggers, and ensure that background tasks are properly managed outside the request/response cycle.