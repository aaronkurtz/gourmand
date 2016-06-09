# gourmand

[![Build Status](https://travis-ci.org/aaronkurtz/gourmand.svg)](https://travis-ci.org/aaronkurtz/gourmand)

### Gourmand - Read until you're full

Gourmand is a social RSS reader designed for mobile and desktop use.

It is implemented using Python 3, the Django web framework, and PostgreSQL.
It is licensed under the GNU General Public License Version 2.


## Setup

Install PostgreSQL and the python3 and libpq development packages.

For the Debian family:

    sudo apt-get install postgres build-essential python3-dev libpq-dev


In a Python virtual environment, install the Python libraries.

    pip install -r gourmand/requirements.txt


Setup the appropriate environmental variables. [Direnv](http://direnv.net/) is one way to do this.

    SECRET_KEY=YOURSECRET
    DATABASE_URL=postgres://DBUSER:PASSWORD@db_address:PORT/dbname
    CACHE_URL=dbcache://gourmand_cache
    DEBUG=True

### Optional 

If gourmand is run behind SSL, non-SSL images will create mixed content messages. Gourmand can use [go-camo](https://github.com/cactus/go-camo) to proxy the images. 


## Environmental variables

### Required

SECRET_KEY, string - The Django secret key - see https://docs.djangoproject.com/en/1.9/ref/settings/#secret-key

CACHE_URL, django-environ cache_url - see https://github.com/joke2k/django-environ for details.

    CACHE_URL=redis://localhost:6379/0  # Redis example

DATABASE_URL, django-environ db_url - see https://github.com/joke2k/django-environ for details.

    DATABASE_URL=postgres://DBUSER:PASSWORD@db_address:PORT/dbname  # Postgres example


### Optional settings
ALLOWED_HOSTS, comma-seperated list of strings - the appropriate hostnames for the site - see https://docs.djangoproject.com/en/1.9/ref/settings/#allowed-hosts. Required if DEBUG is False.

    ALLOWED_HOSTS=gourmand.io,staging.gourmand.io  # Example
    
CAMO_KEY, string - the Camo HMAC key.

CAMO_ADDRESS, hostname/address - the go-camo server's private location. Required if CAMO_KEY is set.

CAMO_PATH, URL - the URL used to construct the public go-camo URLs. Required if CAMO_KEY is set.

DEBUG, Boolean.

OPBEAT, django-environ dict - [Opbeat](https://opbeat.com/) configuration settings for performance monitoring and error reporting. Example:

    OPBEAT=ORGANIZATION_ID=hex,APP_ID=hex,SECRET_TOKEN=hex  # Example

### Vagrant

Test deployment to a [Vagrant](https://www.vagrantup.com/) virtual server is provided through an ansible playbook. Please note that Ansible is Python 2 only, so install it as a system package or install deployment_requirements.txt in a separate virtual environment.

    vagrant up
  
If the deployment succeeds, Gourmand will be available at [http://localhost:8080/](http://localhost:8080/)
