# Air Purrr - back-end

This is a back-end side of my Air Purrr project.

<img src="https://i.imgur.com/krAfhpc.jpg" width="430"> <img src="https://i.imgur.com/cbJ3k2f.jpg" width="430">
<br/><br/>

## Air Purifier components
* [Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/) - The mini-computer with Apache2 server on it
* [Nova Fitness SDS011](https://www.aliexpress.com/item/nova-PM-sensor-SDS011-High-precision-laser-pm2-5-air-quality-detection-sensor-module-Super-dust/32617788139.html?spm=a2g17.10010108.1000016.1.cfbe645O7s0gk&isOrigTitle=true) - PM2.5/10 detector
* ~~[QinHeng Electronics HL-340](https://www.aliexpress.com/item/nova-PM-sensor-SDS011-High-precision-laser-pm2-5-air-quality-detection-sensor-module-Super-dust/32617788139.html?spm=a2g17.10010108.1000016.1.cfbe645O7s0gk&isOrigTitle=true) - default USB-Serial adapter~~ - DON'T use it! It's a buggy device
* [Prolific PL2303](https://www.waveshare.com/product/PL2303-USB-UART-Board-type-A.htm) - use this one (or anything based on, for example, PL2303)!
* 2-channel relay board - to control the fan
* Raspberry Pi's deconstructed 5V/3A charger
* [Case](http://allegro.pl/g750-obudowa-uniwersalna-z-abs-i7025164953.html) - I used this one but could be anything
* [230V fan](http://www.cata.es/en/catalog/a%C3%A9ration/tubular-extraction/duct-in-line/151?_locale=es&_region=lenguage.country.resto.europa) - I used one of these
* Filter mats
* Cables, jumpers etc.
* [SKILL WITH MAINS ELECTRICITY](https://www.youtube.com/watch?v=sskSFYxzkpE) - no joke here, this is a must
<br/><br/>

## First steps
* main Apache2 configuration can be found [here](https://www.digitalocean.com/community/tutorials/how-to-install-the-apache-web-server-on-debian-9)
* for auto-creation of SSL certificate with use of Certbot, please go [here](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-debian-9)
<br/><br/>

## Tips
* ```sudo apt-get install libapache2-mod-wsgi-py3``` for running Python3 codes
* ```sudo pip3 install Flask-BasicAuth && sudo pip3 install flask-bcrypt && sudo pip3 install paho-mqtt``` for missing libraries
* [```echo "ServerName localhost" | sudo tee /etc/apache2/conf-available/servername.conf```, then ```sudo a2enconf servername```](https://askubuntu.com/a/396048) for dismissing a warning while restarting Apache2
* [```sudo usermod -a -G tty www-data && sudo usermod -a -G dialout www-data```](https://askubuntu.com/a/133244) && [```sudo usermod -a -G gpio www-data```](https://raspberrypi.stackexchange.com/a/39191) for granting necessary permissions for Apache2 group
*  ```sudo chmod 666 data.json``` to enable write permissions for ```data.json```
* ```sudo chmod 444 db.txt``` to restrict access for ```db.txt``` (at the end of configuration)
<br/><br/>

## Directories
* ```/etc/apache2/conf-available``` - some SSL configuration
* ```/etc/apache2/sites-available``` - **important server configuration for HTTP and HTTPS respectively**
* ```/etc/ssl/certs``` - SSL certificates location (along with CA bundle certficate, both used above)
* ```/etc/ssl/private``` - SSL private key location
* ```/var/www/airpurrr.eu/flask``` - **server-side code for HTTPS (Flask)**
* ```/var/www/airpurrr.eu/html``` - server-side code for HTTP
* ```/var/log/apache2``` - **logs**
* ```/home/pi/.config/autostart/lxterm-autostart.desktop``` - autostart config
<br/><br/>

## Charts
Data is published on MathWorks' ThingSpeak platform - you can find it [here](https://thingspeak.com/channels/462987).
