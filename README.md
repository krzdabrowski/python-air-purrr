# Air Purrr - backend

<img src="https://raw.githubusercontent.com/krzdabrowski/backend-air-purrr/master/air_purifier.JPG" width="400"> <img src="https://raw.githubusercontent.com/krzdabrowski/backend-air-purrr/master/device_inside.JPG" width="400">
<br/><br/>

## Air Purifier components
* [Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/) - The mini-computer with Apache2 server on it
* [Nova Fitness SDS011](https://www.aliexpress.com/item/nova-PM-sensor-SDS011-High-precision-laser-pm2-5-air-quality-detection-sensor-module-Super-dust/32617788139.html?spm=a2g17.10010108.1000016.1.cfbe645O7s0gk&isOrigTitle=true) - PM2.5/10 detector
* ~~[QinHeng Electronics HL-340](https://www.aliexpress.com/item/nova-PM-sensor-SDS011-High-precision-laser-pm2-5-air-quality-detection-sensor-module-Super-dust/32617788139.html?spm=a2g17.10010108.1000016.1.cfbe645O7s0gk&isOrigTitle=true) - default USB-Serial adapter~~ - DON'T use it! It's a buggy device
* [Prolific PL2303](https://www.waveshare.com/product/PL2303-USB-UART-Board-type-A.htm) - use this one (or anything based on, for example, PL2303)!
* [4-channel relay board](https://botland.com.pl/pl/przekazniki/2579-modul-przekaznikow-4-kanaly-z-optoizolacja-styki-10a250vac-cewka-5v.html) - to control the fan control voltage and its gear
* Raspberry Pi's deconstructed 5V/3A charger
* [Case](http://allegro.pl/g750-obudowa-uniwersalna-z-abs-i7025164953.html) - I used this one but could be anything
* [230V fan](http://www.cata.es/en/catalog/a%C3%A9ration/tubular-extraction/duct-in-line/151?_locale=es&_region=lenguage.country.resto.europa) - I used one of these
* Filter mats
* Cables, jumpers etc.
* [SKILL WITH MAINS ELECTRICITY](https://www.youtube.com/watch?v=sskSFYxzkpE) - no joke here, this is a must
<br/><br/>

## Architecture

Whole architecture is now based using Mikrotik pre-configured router:
* OpenVPN as VPN service
* local DNS service for modules' local addresses

Moreover, most of data communication uses MQTT protocol along with publish-subscribe pattern.

Encryption and server-side-related operations is done by network's configuration and it's not a part of this repository.
