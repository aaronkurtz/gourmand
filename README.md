# gourmand

### Gourmand - Read until you're full

Gourmand is a social RSS reader designed for mobile and desktop use.

It is implemented using Python 3, the Django web framework, and PostgreSQL.
It is licensed under the GNU General Public License Version 2.


## Setup

Install PostgreSQL and the python3 and libpq development packages.

For the Debian family:
  sudo apt-get install postgres python3-dev libpq-dev


In a virtual environment, install the Python libraries.
  pip install -r requirements.txt


Setup the required environmental variables. Direnv (http://direnv.net/) is one way to do this.
  SECRET_KEY=YOURSECRET
  DATABASE_URL=postres://DBUSER:PASSWORD@db.address:PORT?ATOMIC_REQUESTS=True
  DEBUG=True
