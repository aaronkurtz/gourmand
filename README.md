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


Setup the required environmental variables. Direnv (http://direnv.net/) is one way to do this.

    SECRET_KEY=YOURSECRET
    DATABASE_URL=postgres://DBUSER:PASSWORD@db_address:PORT/dbname
    CACHE_URL=dbcache://gourmand_cache
    DEBUG=True

### Vagrant

Test deployment to a [Vagrant](https://www.vagrantup.com/) virtual server is provided through an ansible playbook. Please note that Ansible is Python 2 only, so install it as a system package or install deployment_requirements.txt in a separate virtual environment.

    vagrant up
  
If the deployment succeeds, Gourmand will be available at [http://localhost:8080/](http://localhost:8080/)
