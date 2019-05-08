# Air Purrr - back-end

This is a back-end side of my Air Purrr project. Keep in mind that some codes might need some improvements/refactoring in the future.

## Self-made Air Purifier

It uses:
* [Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/) - The mini-computer with Apache2 server on it
* [Nova Fitness SDS011](https://www.aliexpress.com/item/nova-PM-sensor-SDS011-High-precision-laser-pm2-5-air-quality-detection-sensor-module-Super-dust/32617788139.html?spm=a2g17.10010108.1000016.1.cfbe645O7s0gk&isOrigTitle=true) - PM2.5/10 detector
* ~~[QinHeng Electronics HL-340](https://www.aliexpress.com/item/nova-PM-sensor-SDS011-High-precision-laser-pm2-5-air-quality-detection-sensor-module-Super-dust/32617788139.html?spm=a2g17.10010108.1000016.1.cfbe645O7s0gk&isOrigTitle=true) - default USB-Serial adapter~~ - DON'T use it! unless you want to have some uncool bugs
* [Prolific PL2303](https://www.waveshare.com/product/PL2303-USB-UART-Board-type-A.htm) - use this one (or anything based on PL2303)! it seems bug-free for now
* 2-channel relay board - to control the fan
* Raspberry Pi's deconstructed 5V/3A charger
* [Case](http://allegro.pl/g750-obudowa-uniwersalna-z-abs-i7025164953.html) - I used this one but could be anything
* [230V fan](http://www.cata.es/en/catalog/a%C3%A9ration/tubular-extraction/duct-in-line/151?_locale=es&_region=lenguage.country.resto.europa) - I used one of these
* Cables, jumpers etc.
* Filter mats
* [SKILL WITH MAINS ELECTRICITY](https://www.youtube.com/watch?v=sskSFYxzkpE) - no joke here, this is a must

## Files protips

### RPi autostart
* create this file to launch any script at startup: ```/home/pi/.config/autostart/lxterm-autostart.desktop```

### Server-side code (Flask)
* use ```chmod 755``` in ```flask-prod``` directory
* don't use ```redirect()``` in Flask - it worked in Postman but didn't work in an Android app

### Server configuration (Apache2)
* use Step 2 and Step 4 from [here](https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-apache-in-ubuntu-16-04) to configure basic SSL modules
* use ```libapache2-mod-wsgi-py3``` for Python3 codes
* use ```WSGIPassAuthorization On``` in ```sites-available/default-ssl.conf``` to pass auth header
* use ```WSGIDaemonProcess threads=25``` and ```processes=2``` in ```sites-available/default-ssl.conf```
* current info about Apache2 configuration [here](https://www.digitalocean.com/community/tutorials/how-to-install-the-apache-web-server-on-debian-9)
* *for future [read](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-debian-9) about auto-renew SSL certs with certbot (or [this](https://www.splitbrain.org/blog/2016-05/14-simple_letsencrypt_on_debian_apache))*

## Directories cheatsheet
* ```/etc/apache2/conf-available``` for ```ssl-params.conf``` - some SSL configuration
* ```/etc/apache2/sites-available``` for ```000-default.conf``` and ```default-ssl.conf``` - **important server configuration for HTTP and HTTPS respectively**
* ```/etc/ssl/certs``` - **SSL certificates location** (along with CA bundle certficate, both used above)
* ```/etc/ssl/private``` - SSL private key location
* ```/var/www/flask-prod``` - **server-side code for HTTPS (Flask)**
* ```/var/www/html``` - server-side code for HTTP (plain PHP)
* ```/var/log/apache2``` - ```access.log``` and ```error.log``` logs

## SDS011 PM2.5/10 Results

I use ThingSpeak to show data from my device. Here's the [link](https://thingspeak.com/channels/462987) to charts.
