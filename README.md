# MarinaNet Setup
___

## Create a Virtual Environment and install requirements
1. Create a directory for the project:
```
$ mkdir marinachain
$ cd marinachain
```
2. Create a [Python Virtual Environment](https://docs.python.org/3/library/venv.html):
```
$ python3 -m venv env
```
3. Activate the Virtual Environment:
```
$ source env/bin/activate
```
4. Clone the repository:
```
$ git clone ssh://git-codecommit.ap-southeast-1.amazonaws.com/v1/repos/marinanet-backend
```
5. Intall the required packages:
```
$ cd marinanet-backend
$ pip install -r requirements.txt
```

## Install and setup Redis, PostgreSQL, and PostGIS
1. If you are on MacOS, make sure you have the [Homebrew](https://brew.sh/) package manager installed.
2. Using Homebrew, install and start Postgres:
```
$ brew install redis
$ brew install postgresql
$ brew install postgis
$ brew install gdal
$ brew install libgeoip
$ brew services start postgresql
```
3. Start the Postgres interactive terminal:
```
$ psql postgres
```
3. Create a database called `marinanet` on Postgres, then create a user and grant it privileges to modify and write to the database:
```
# CREATE DATABASE marinanet;
# CREATE USER marinanet WITH PASSWORD 'correcthorsebatterystaple';
# GRANT ALL PRIVILEGES ON DATABASE marinanet TO marinanet;
```
4. `CTRL-D` to exit the Postgres shell.
5. Enable PostGIS functionality on Postgres:
```
$ psql marinanet

# CREATE EXTENSION postgis;
```
6. `CTRL-D` to exit the Postgres shell.

## Setup and run the Django Backend
1. Get a copy of `secrets.py` from another team member. This file contains all all the secrets related to the project, such as usernames, passwords, and API Keys. **DO NOT CIRCULATE THIS FILE!**
2. Update your Postgres username and password in this file so Django can connect to your database.
3. Run the database migrations needed for the project:
```
$ python manage.py migrate
```
4. In a separate terminal, run the Redis server:
```
$ source env/bin/activate
$ redis-server
```
5. In a separate terminal, run Celery:
```
$ source env/bin/activate
$ python -m celery -A marinanet worker
```
6. Run the local Django development server:
```
$ python manage.py runserver
```
7. Using your browser or Postman, navigate to `localhost:8000/api/public` and see if it works.
