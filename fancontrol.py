#!/usr/bin/env python3

import subprocess
import time

from gpiozero import PWMLED


TEMP_MIN = 55 # Temperature (or lower) where fan voltage is 0.0
TEMP_MAX = 65 # Temperature (or higher) where van voltage is 1.0
SLEEP_INTERVAL = 5  # (seconds) How often we check the core temperature.
GPIO_PIN = 17  # Which GPIO pin you're using to control the fan.
HIGH_PERCENT = 0.6
LOW_PERCENT = 0.4


def get_temp():
    """Get the core temperature.

    Run a shell script to get the core temp and parse the output.

    Raises:
        RuntimeError: if response cannot be parsed.

    Returns:
        float: The core temperature in degrees Celsius.
    """
    output = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True)
    temp_str = output.stdout.decode()
    try:
        return float(temp_str.split('=')[1].split('\'')[0])
    except (IndexError, ValueError):
        raise RuntimeError('Could not parse temperature output.')

def get_voltage():
    r = TEMP_MAX - TEMP_MIN # delta consigne
    dv = HIGH_PERCENT - LOW_PERCENT
    step = dv / r
    v = get_temp() - TEMP_MIN
    if v <= 0:
        return 0
    v = LOW_PERCENT + (v * step)
    if v > 1:
        return 1
    return v

if __name__ == '__main__':
    # Validate
    if TEMP_MIN >= TEMP_MAX:
        raise RuntimeError('TEMP_MIN must be less than TEMP_MAX')

    fan = PWMLED(GPIO_PIN)
    fan.on()
    fan_on = False
    fan.value = 0
    temp_seuil = (TEMP_MAX + TEMP_MIN) / 2

    while True:
        temp = get_temp()
        if not fan_on and temp > temp_seuil:
            fan_on = True
        if temp < TEMP_MIN:
            fan_on = False
            fan.value = 0
        if fan_on: 
            voltage = get_voltage()
            fan.value = voltage
        # print(u'temp: {} voltage: {}'.format(temp, fan.value))
        time.sleep(SLEEP_INTERVAL)
