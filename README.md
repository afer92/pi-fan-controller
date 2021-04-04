# Pi Fan Controller

Raspberry Pi fan controller.

## Description

This repository provides scripts that can be run on the Raspberry Pi that will
monitor the core temperature and start the fan when the temperature reaches
a certain threshold.

To use this code, you'll have to install a fan. The full instructions can be
found on our guide: [Control Your Raspberry Pi Fan (and Temperature) with Python](https://howchoo.com/g/ote2mjkzzta/control-raspberry-pi-fan-temperature-python).

## Usage

```
usage: fancontrol.py [-h] [-i] [-v] [-m TEMP_MIN] [-M TEMP_MAX]
                     [-p PERCENT_LOW] [-P PERCENT_HIGH] [-t TEST]

optional arguments:
  -h, --help            show this help message and exit
  -i, --infos           print parameters, tempcpu and voltage
  -v, --verbose         verbose
  -m TEMP_MIN, --temp_min TEMP_MIN
                        TEMP_MIN
  -M TEMP_MAX, --temp_max TEMP_MAX
                        TEMP_MAX
  -p PERCENT_LOW, --percent_low PERCENT_LOW
                        LOW_PERCENT
  -P PERCENT_HIGH, --percent_high PERCENT_HIGH
                        HIGH_PERCENT
  -t TEST, --test TEST  run TEST cycles and display temperature and voltage
  ```

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
LOW_PERCENT :   0.4% (2.0V)
HIGH_PERCENT :  0.6% (3.0V)
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
