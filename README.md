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
