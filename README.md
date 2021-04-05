![pylint Score](https://raw.githubusercontent.com/afer92/pi-fan-controller/78a972e18da4a190d55bf63acd713b498f845ca5/pylint.svg)
# Pi Fan Controller

Raspberry Pi fan controller.

## Description

This repository provides scripts that can be run on the Raspberry Pi that will
monitor the core temperature and start the fan when the temperature reaches
a certain threshold.

To use this code, you'll have to install a fan. The full instructions can be
found on our guide: [Control Your Raspberry Pi Fan (and Temperature) with Python](https://howchoo.com/g/ote2mjkzzta/control-raspberry-pi-fan-temperature-python).

## Usage

```sh
$ ./fancontrol.py -h
usage: fancontrol.py [-h] [-i] [-v] [-V] [-m TEMP_MIN] [-M TEMP_MAX]
                     [-p PERCENT_LOW] [-P PERCENT_HIGH] [-G GPIO_PIN]
                     [-t TEST] [-s SLEEP_INTERVAL]

optional arguments:
  -h, --help            show this help message and exit
  -i, --infos           print parameters, tempcpu and voltage (default: False)
  -v, --verbose         verbose (default: False)
  -V, --version         program version (default: False)
  -m TEMP_MIN, --temp_min TEMP_MIN
                        temp_min °C (default: 40)
  -M TEMP_MAX, --temp_max TEMP_MAX
                        temp_max °C (default: 50)
  -p PERCENT_LOW, --percent_low PERCENT_LOW
                        percent_low % (default: 0.4)
  -P PERCENT_HIGH, --percent_high PERCENT_HIGH
                        percent_high % (default: 0.6)
  -G GPIO_PIN, --gpio_pin GPIO_PIN
                        gpio_pin (default: 17)
  -t TEST, --test TEST  run test cycles and display temperature and voltage
                        (default: False)
  -s SLEEP_INTERVAL, --sleep_interval SLEEP_INTERVAL
                        sleep_interval seconds (default: 5)
  ```

## Parameters

>          1 ( 5V )                  ___________
>                                  /
>          PERCENT_HIGH-----------/ (default: 0.6)
>                                /|
>                               / |
>                              /  |
>                             /  TEMP_MAX (default: 50)
>                            /
>          PERCENT_LOW------/  (default: 0.4)
>                          /|
>                         / |
>                        /  |
>          0 ___________/  TEMP_MIN (default: 40)
>         
>          threshold : (TEMP_MAX + TEMP_MIN)/2
>
>          fan start = temp_cpu > threshold (default: 45°C)
>          fan stop  = temp_cpu < TEMP_MIN (default: 40°C)

## supervisor

```
sudo apt-get install supervisor
```
[How to configure supervisor](http://supervisord.org/configuration.html)

fancontrol.sh
```
#!/bin/sh

/usr/bin/python3 /usr/local/bin/fancontrol.py -m 40 -M 45 -p 0.4 -P 0.6 -v -t 60 > /home/pi/scripts/system/fancontrol.log

exit 0
```

fancontrol.conf
```
[program:fancontrol]
command=/home/pi/scripts/system/fancontrol.sh
autostart=true
autorestart=true
startretries=3
```
Log:

```
cat /home/pi/scripts/system/fancontrol.log
GPIO_PIN :      17
SLEEP :         5s
TEMP_MIN :      40°C
TEMP_MAX :      45°C
PERCENT_LOW :   0.4% (2.0V)
PERCENT_HIGH :  0.6% (3.0V)
CPU_TEMP :      41.3°C
VOLTAGE :       0.45% (2.26V)
temp: 42.3 voltage: 0.0
temp: 41.3 voltage: 0.0
temp: 41.8 voltage: 0.0
temp: 41.8 voltage: 0.0
temp: 41.8 voltage: 0.0
temp: 43.8 voltage: 0.5319999999999999
temp: 42.8 voltage: 0.5719999999999998
temp: 43.8 voltage: 0.5319999999999999
temp: 43.3 voltage: 0.5719999999999998
```
