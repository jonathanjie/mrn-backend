# Deployment Guide
___
This guide is for deployment of the Django Backend on an AWS EC2 instance running Ubuntu 22.04.
A PostgreSQL 14 database should also be set up to run on AWS RDS.

___
## Logging into EC2
1. Make sure you have the private key to log into EC2. It should end in `.pem`.
2. Using the private key, SSH into the EC2 instance.
```
$ ssh -i .ssh/mctech.pem ubuntu@<EC2 instance Public IPv4 DNS>
```

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
## Connect to PostgreSQL on AWS RDS
1. Install the PostgreSQL 14 client.
```
$ sudo apt install postgresql-client-common postgresql-client-14
```
2. Log in as the Postgres superuser. Get the DB Host details from the AWS RDS console.
```
$ psql --host=<DB Host> --port=5432 --username=postgres
```
3. Create a database called `marinanet` on Postgres, then create a user and grant it privileges to modify and write to the database:
```
# CREATE DATABASE marinanet;
# CREATE USER marinanetuser WITH PASSWORD 'correcthorsebatterystaple';
# GRANT rds_superuser TO mnetadmin;
# GRANT ALL PRIVILEGES ON DATABASE marinanet TO marinanetuser;
```
4. `CTRL-D` to exit the Postgres shell.
5. Enable PostGIS functionality on Postgres:
```
$ $ psql --host=<DB Host> --port=5432 --username=marinanetuser
# CREATE EXTENSION postgis;
```
6. `CTRL-D` to exit the Postgres shell.
7. `CTRL-D` to logout of the Postgres superuser.

If you are unable to log in as `marinanetuser`:
```
$ psql --host=<DB Host> --port=5432 --username=postgres
# ALTER ROLE marinanetuser WITH LOGIN;
```
`CTRL-D` to logout of the Postgres superuser.


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
1. In your home directory, create a [Python Virtual Environment](https://docs.python.org/3/library/venv.html):
```
$ python3 -m venv env
```
2. Activate the Virtual Environment:
```
$ source env/bin/activate
```
3. Clone the repository: (You may need to setup your SSH keys before cloning)
```
$ git clone ssh://git-codecommit.ap-southeast-1.amazonaws.com/v1/repos/marinanet-backend
```
4. Intall the required packages:
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
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/marinanet-backend
ExecStart=/home/unbuntu/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          marinanet.wsgi:application

[Install]
WantedBy=multi-user.target
```
8. Start the Gunicorn service.
```
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
```
9. Configure Nginx using [DigitalOcean's Nginx Configuration Tool](https://www.digitalocean.com/community/tools/nginx). Select the appropriate settings (Domain, User, Gunicorn instead of uWSGI), download the configuration files, and execute the commands as given. This should get you setup for https on the chosen domain.

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
- [Setting Up PostGIS on AWS RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.PostgreSQL.CommonDBATasks.PostGIS.html)
- [GeoDjango Installation](https://kitcharoenp.github.io/gis/2018/06/12/geodjango_installation.html)
- [Gunicorn and Nginx Setup (DigitalOcean)](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04)
- [Gunicorn and Nginx Setup (CloudSigma)](https://www.cloudsigma.com/setting-up-django-with-postgresql-nginx-and-gunicorn-on-ubuntu-20-04/)
- [DigitalOcean's Nginx Configuration Tool](https://www.digitalocean.com/community/tools/nginx)
- [Setting Up SSH Connections to AWS CodeCommit](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-ssh-unixes.html)
