# Deployment Guide
___
This guide has been tested on Ubuntu 22.04.

___
## Update Packages
1. Update package repository, upgrade existing packages, and reboot.
```
$ sudo apt update
$ sudo apt upgrade
$ reboot
```
2. Install PIP, the Python package manager and Virtual Environment module.
```
$ sudo apt install python3-pip python3-venv
```
3. Install Git.
```
$ sudo apt install git
```
4. Configure Git.
```
$ git config --global user.name "Bobby Tables"
$ git config --global user.email "bobby@marinachain.io"
$ git config pull.rebase false
```

___
## Install and setup PostgreSQL and PostGIS
1. Import the PostgreSQL repository key, and add the repository.
```
$ sudo apt install curl ca-certificates gnupg
$ curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/apt.postgresql.org.gpg >/dev/null
$ echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list
$ sudo apt update
```
2. Install PostgreSQL 14.
```
$ sudo apt install postgresql-14 postgresql-client-14
```
3. Install PostGIS 3.
```
$ sudo apt install postgis postgresql-14-postgis-3
```
4. Install required control packages.
```
$ sudo apt-get install postgresql-14-postgis-3-scripts
```
5. Log in as the Postgres superuser.
```
$ sudo su - postgres
```
6. Start the Postgres interactive terminal:
```
$ psql postgres
```
7. Create a database called `marinanet` on Postgres, then create a user and grant it privileges to modify and write to the database:
```
# CREATE DATABASE marinanet;
# CREATE USER marinanetuser WITH PASSWORD 'correcthorsebatterystaple';
# GRANT ALL PRIVILEGES ON DATABASE marinanet TO 'marinanetuser';
```
8. `CTRL-D` to exit the Postgres shell.
9. Enable PostGIS functionality on Postgres:
```
$ psql marinanet
# CREATE EXTENSION postgis;
```
10. `CTRL-D` to exit the Postgres shell.
11. `CTRL-D` to logout of the Postgres superuser.

___
## Install Geospatial Libraries
1. Install the required Geospatial libaries for GeoDjango.
```
$ sudo apt-get install binutils libproj-dev gdal-bin
```
2. Install the GEOS API.
```
$ sudo apt-get install libgeos++
```
3. Install Proj4.
```
$ sudo apt-get install proj-bin
```
4. Install the GDAL API.
```
$ sudo apt install gdal-bin
```

___
## Create a Virtual Environment and install requirements
1. In your home directory, create a directory for the project:
```
$ cd
$ mkdir marinachain
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

___
## Setup and run the Django Backend
1. Get a copy of `secrets.py` from another team member. This file contains all all the secrets related to the project, such as usernames, passwords, and API Keys. **DO NOT CIRCULATE THIS FILE!**
2. Update your Postgres username and password in this file so Django can connect to your database.
3. Run the database migrations needed for the project:
```
$ python manage.py migrate
```
4. Run the local Django development server:
```
$ python manage.py runserver
```
5. Using your browser or Postman, navigate to `localhost:8000/api/public` and see if it works.

___
## Deploy site with Gunicorn and Nginx
1. Install Gunicorn.
```
$ pip install gunicorn
```
2. Install Nginx.
```
$ sudo apt install nginx
```
3. Collect static files for deployment.
```
$ python manage.py collectstatic
```
4. Create Gunicorn socket.
```
$ sudo vim /etc/systemd/system/gunicorn.socket
```
5. Enter the following in the file and save.
```
[Unit]
Description=gunicorn socket
[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```
6. Create a systemd service file for Gunicorn.
```
sudo vim /etc/systemd/system/gunicorn.service
```
7. Enter the following code and save.
```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=cloudsigma
Group=www-data
WorkingDirectory=/home/bobby/marinachain/marinanet-backet
ExecStart=/home/bobby/marinachain/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          viktor_project.wsgi:application

[Install]
WantedBy=multi-user.target
```
8. Start the Gunicorn service.
```
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
```
9. Configure Nginx using [DigitalOcean's Nginx Configuration Tool](https://www.digitalocean.com/community/tools/nginx). Select the appropriate settings, download the configuration files, and execute the commands as given. This should get you setup for https on the chosen domain.

Note:
- If you make any changes to the Gunicorn service file, you will need to reload the service.
```
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```
- If you make any changes to the Nginx configuration files, you will need to reload Nginx.
```
sudo nginx -t
sudo systemctl reload nginx
```
___
## References
- [PostgreSQL Ubuntu Download](https://www.postgresql.org/download/linux/ubuntu/)
- [PostgreSQL Apt Repository](https://wiki.postgresql.org/wiki/Apt)
- [PostGIS Installation](https://www.vultr.com/docs/install-the-postgis-extension-for-postgresql-on-ubuntu-linux/)
- [GeoDjango Installation](https://kitcharoenp.github.io/gis/2018/06/12/geodjango_installation.html)
- [Gunicorn and Nginx Setup (DigitalOcean)](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04)
- [Gunicorn and Nginx Setup (CloudSigma)](https://www.cloudsigma.com/setting-up-django-with-postgresql-nginx-and-gunicorn-on-ubuntu-20-04/)
- [DigitalOcean's Nginx Configuration Tool](https://www.digitalocean.com/community/tools/nginx)
