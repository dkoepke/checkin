# checkin

A tiny service that records location checkins

## Setting up on Ubuntu

Create an RDS PostgreSQL instance that can be connected to from your server, then:

```
sudo apt-get install -y python-setuptools postgresql-client libpq-dev
sudo easy_install pip
sudo pip install virtualenv
virtualenv env
env/bin/pip install -r requirements.txt
```

The database is configured with the following environment variables:

* `CHECKIN_DB_HOST` is the DB host; it defaults to `localhost`
* `CHECKIN_DB_PORT` is the DB port; it defaults to `5432`
* `CHECKIN_DB_USER` is the DB user
* `CHECKIN_DB_PASSWORD` is the DB password for the given DB user

The admin interface is configured with the following environment variables:

* `CHECKIN_ADMIN_USER`
* `CHECKIN_ADMIN_PASSWORD`

Set the above environment variables to whatever is appropriate from your RDS configuration and then run the app:

```
gunicorn -w 4 -b 0.0.0.0:9000 checkin:app
```

In reality, you'll want to deploy gunicorn behind Nginx, with Nginx talking to gunicorn over a UNIX socket. Configuring gunicorn and Nginx is beyond the scope of this document.
