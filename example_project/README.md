# Running the captive portal

We assume that you are using Debian Stretch or Buster.
Install the dependencies with APT:

```bash
# apt install python3-django python3-dateutil python3-django-reversion python3-pip
```

Then install the remaining dependencies with PIP:

```bash
# pip3 install django-bootstrap3 django-macaddress
```

Clone the project (can be in `/var/local`):

```bash
$ git clone https://gitlab.com/erdnaxe/captivitate.git
$ cd captivitate/example_project
```

Now we need to create the database tables and an admin user.
Run the following and when prompted to create a
superuser choose yes and follow the instructions:

```bash
$ python3 manage.py migrate
$ python3 manage.py createsuperuser
```

Now you need to run the Django development server:

```
$ python3 manage.py runserver
```

You should then be able to open your browser on <http://127.0.0.1:8000> and see
captivitate running.

## For a production environment

You should use PostgreSQL (`psycopg2` and `postgresql` packages)
or MySQL (`python3-mysqldb`, `mysql-client` and `mysql-server` packages).

For MySQL, use the following to create a database:

```SQL
CREATE DATABASE portail_captif;
CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON portail_captif.* TO 'newuser'@'localhost';
FLUSH PRIVILEGES;
```
