Splitpot
========
# Usage
Use 'python App.py' from root dir, to start the server with the default configuration

# Installation
Prerequisites:
- Running Apache
- Git installed

**1. Install python**

```sudo apt-get install python python-dev python-setuptools```

**2. Install sqlite3**

```sudo apt-get install sqlite3```

**3. Install mako**

```sudo apt-get install python-mako```

**4. Install Cherrypy**
```
wget http://download.cherrypy.org/CherryPy/3.2.2/CherryPy-3.2.2.tar.gz
tar -zxvf CherryPy-3.2.2.tar.gz
cd CherryPy-3.2.2
python setup.py install
```

**5. Checkout the latest Splitpot source from GitHub**

Let's say you're in /var/www/ run ```sudo git clone git@github.com:toebbel/splitpot.git```
/var/www/splitpot is now your local Splitpot root.

**6. Config Splitpot to run behind proxy-mode of apache**

Enable mod_proxy for apache 2

```sudo a2enmod proxy_http```

Edit ```/etc/apache2/sites-enabled/000-default```
and add the following:
```
ProxyPreserveHost on
<Proxy *>
  Order allow,deny
  Allow from all
</Proxy>
ProxyPass /splitpot/ http://127.0.0.1:8080/splitpot/
ProxyPassReverse /splitpot/ http://127.0.0.1:8080/splitpot/
```
Restart your apache

```sudo /etc/init.d/apache2 restart```

**7. Config mail settings**

```cp resource/mail.settings.template resource/mail.settings```

Then fill ```resource/mail.settings``` with the appropriate mail settings.

To fill/reset the database with test data:
* run ```script/reset_database.sh``` from splitpot's root directory
* Database contains nothing except for one user: Use login awesome@0xabc.de : awesome
* 
* //TODO setup user and cron jobs

# Unittesting
* start all tests via 'python -m unittest discover' (in root dir)
  * in some cases one has to specifiy the file name: python -m unittest discover -p 'Test*.py' 
* start a specific test via 'python test/TestName.py' (in root dir)
* more infos: http://docs.python.org/2/library/unittest.html
