# Stock-Market-Simulation

## Features

+ Python
+ FastAPI
+ Postgres
+ celery
+ Redis
+ Apache Kafka
+ Pytest
+ Docker
+ Sentry for monitoring the app
+ Celery flower for monitoring the Celery tasks
+ Alembic for Database Migrations
+ pre-commit hooks

## 1. Clone the repository
```shell
git clone git@github.com:codegeek010/Stock-Market-Simulation.git
```

## Docker Setup
Create a `.env` file and set database url's
```shell
cp .env-docker .env
```
Build and start Docker Services
```shell
sudo docker-compose up --build -d
```
Run alembic migrations
```shell
sudo docker-compose run app alembic upgrade head
```
Run Generate Stocks script
```shell
sudo docker-compose exec app bash
PYTHONPATH=. python scripts/genrate-stock-data.py
```

## Non Docker environment setup
### 2. Virtual environment
Create and activate virtual environment:
```shell
cd Stock-Market-Simulation
python3 -m venv env
source env/bin/activate
```

### 3. Create a `.env` file
```shell
cp .env-sample .env
```
Note: set .env values according to your local configurations.

### 4. Database migration
Note: If you are running the app with PostgreSQL, you will probably need to
create the databases as well:
```shell
createdb --host=localhost -U postgres -O postgres -E utf8 -T template0 stock_market_simulation
createdb --host=localhost -U postgres -O postgres -E utf8 -T template0 stock_market_simulation_test
```

### 5. Install the required modules:
```shell
bash ./setup.sh
```

### 6. Start the Application

```shell
bash run.sh
```
The API will be accessible at [http://localhost:8000](http://localhost:8000).

### 7. Run celery worker
```shell
celery -A celery_service.celery worker --loglevel=info
```

### 8. Run celery flower
```shell
celery -A celery_service.celery flower
```

### 8. Run Generate Stocks Data Script
```shell
PYTHONPATH=. python scripts/genrate-stock-data.py
```

### 9. API Documentation
Find swagger docs at [http://127.0.1:8000/docs/swagger](http://127.0.0.1:8000/docs/swagger).

Find flower dashboard at [http://127.0.1:5555](http://127.0.0.1:5555).

To access the Swagger documentation and test the endpoints, visit [http://localhost:8000/docs](http://localhost:8000/docs) and [http://localhost:8000/redoc](http://localhost:8000/redoc) in your web browser.
The Swagger UI provides an interactive interface to explore the API, view the available endpoints, and test their functionalities.

Make sure the API server is running before accessing the Swagger UI.

### 10  . Tests
To run test, run the following command
```shell
pytest -vv -s
```
