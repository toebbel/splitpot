splitpot
========
# Usage
use 'python App.py' from root dir, to start the server wit the default configuration

# Installation
... coming soon
requires: 
* sqlite3
* cherrypy
* mako

To fill/reset the database with test data:
* resource/reset_database.sh
* Database contains some data. Use login awesome@0xabc.de : awesome

# Unittesting
* start all tests via 'python -m unittest discover' (in root dir)
  * in some cases one has to specifiy the file name: python -m unittest discover -p 'Test*.py' 
* start a specific test via 'python test/TestName.py' (in root dir)
* more infos: http://docs.python.org/2/library/unittest.html
