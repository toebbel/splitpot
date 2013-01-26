splitpot
========
# Usage
use 'python App.py' from root dir, to start the server wit the default configuration

# Installation
Prequesites:
- Running Apache
- Git installed

**1. Instal python**
```sudo apt-get install python python-dev python-setuptools```

**2. Install sqlite3**
```sudo apt-get install sqlite3```

**3. Instal lmako**
```sudo apt-get install python-mako```

**4. Install Cherrypy**
```
wget http://download.cherrypy.org/CherryPy/3.2.2/CherryPy-3.2.2.tar.gz
tar -zxvf CherryPy-3.2.2.tar.gz
cd CherryPy-3.2.2
python setup.py install
```

**5. Checkout the latest splitpot source from git**
let's say you're in /var/www/ run ```sudo git clone git@github.com:toebbel/splitpot.git```
/var/www/splitpot is now your local splitpot root.

**6. Config Splitpot to run behind proxy-mode of apache**
enable mod_proxy for apache 2
```sudo a2enmod proxy_http```

edit '/etc/apache2/sites-enabled/000-default'
add the following:
```
ProxyPreserveHost on
<Proxy *>
  Order allow,deny
  Allow from all
</Proxy>
ProxyPass /webapp/ http://127.0.0.1:8080/splitpot/
ProxyPassReverse /webapp/ http://127.0.0.1:8080/splitpot/
```
restart your apache
```sudo /etc/init.d/apache2 restart```

To fill/reset the database with test data:
* run ```script/reset_database.sh``` from splitpot's root directory
* Database contains nothin except one user: Use login awesome@0xabc.de : awesome
* 
* //TODO setup user and cron jobs

# Unittesting
* start all tests via 'python -m unittest discover' (in root dir)
  * in some cases one has to specifiy the file name: python -m unittest discover -p 'Test*.py' 
* start a specific test via 'python test/TestName.py' (in root dir)
* more infos: http://docs.python.org/2/library/unittest.html
