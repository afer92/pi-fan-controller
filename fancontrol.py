#!/usr/bin/env python3

import subprocess
import time

from gpiozero import PWMLED


TEMP_MIN = 40 # Temperature (or lower) where fan voltage is 0.0
TEMP_MAX = 49 # Temperature (or higher) where van voltage is 1.0
SLEEP_INTERVAL = 2  # (seconds) How often we check the core temperature.
GPIO_PIN = 18  # Which GPIO pin you're using to control the fan.


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
    r = TEMP_MAX - TEMP_MIN
    v = get_temp() - TEMP_MIN
    v = v / r
    if v < 0.0001: return 0.0
    elif v > 0.9998: return 1.0
    else: return v

if __name__ == '__main__':
    # Validate
    if TEMP_MIN >= TEMP_MAX:
        raise RuntimeError('TEMP_MIN must be less than TEMP_MAX')

    fan = PWMLED(GPIO_PIN)
    fan.on()

    while True:
        fan.value = get_voltage()
        time.sleep(SLEEP_INTERVAL)
