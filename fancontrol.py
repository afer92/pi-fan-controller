#!/usr/bin/env python3
import argparse
import subprocess
import time

from gpiozero import PWMLED


TEMP_MIN = 40  # Temperature (or lower) where fan voltage is 0.0
TEMP_MAX = 50  # Temperature (or higher) where van voltage is 1.0
SLEEP_INTERVAL = 5  # (seconds) How often we check the core temperature.
GPIO_PIN = 17  # Which GPIO pin you're using to control the fan.
HIGH_PERCENT = 0.6
LOW_PERCENT = 0.4
TEST = False


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
    r = TEMP_MAX - TEMP_MIN  # delta consigne
    dv = HIGH_PERCENT - LOW_PERCENT
    step = dv / r
    v = get_temp() - TEMP_MIN
    if v <= 0:
        return 0
    v = LOW_PERCENT + (v * step)
    if v > 1:
        return 1
    return v


def print_infos():
    print(u'GPIO_PIN : \t{}'.format(GPIO_PIN))
    print(u'SLEEP : \t{}s'.format(SLEEP_INTERVAL))
    print(u'TEMP_MIN : \t{}°C'.format(TEMP_MIN))
    print(u'TEMP_MAX : \t{}°C'.format(TEMP_MAX))
    print(u'LOW_PERCENT : \t{}% ({}V)'.format(LOW_PERCENT, LOW_PERCENT*5))
    print(u'HIGH_PERCENT : \t{}% ({}V)'.format(HIGH_PERCENT, HIGH_PERCENT*5))
    print(u'CPU_TEMP : \t{}°C'.format(get_temp()))
    percent = get_voltage()
    print(u'VOLTAGE : \t{:.2f}% ({:.2f}V)'.format(percent, percent*5))


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infos",
                        help="print parameters, tempcpu and voltage",
                        action="store_true")
    parser.add_argument("-v", "--verbose",
                        help="verbose",
                        action="store_true")
    parser.add_argument("-m", "--temp_min",
                        help="TEMP_MIN", type=int)
    parser.add_argument("-M", "--temp_max",
                        help="TEMP_MAX", type=int)
    parser.add_argument("-p", "--percent_low",
                        help="LOW_PERCENT", type=float)
    parser.add_argument("-P", "--percent_high",
                        help="HIGH_PERCENT", type=float)
    parser.add_argument("-t", "--test",
                        help="test with parameters", type=int)
    args = parser.parse_args()

    if args.infos:
        print_infos()
        exit(0)

    global TEMP_MIN
    global TEMP_MAX
    global LOW_PERCENT
    global HIGH_PERCENT

    if args.temp_min:
        TEMP_MIN = args.temp_min
    if args.temp_max:
        TEMP_MAX = args.temp_max
    if args.percent_low:
        LOW_PERCENT = args.percent_low
    if args.percent_high:
        HIGH_PERCENT = args.percent_high

    # Validate
    if TEMP_MIN >= TEMP_MAX:
        raise RuntimeError('TEMP_MIN must be less than TEMP_MAX')

    if args.verbose:
        print_infos()

    count = 1
    if args.test:
        count = args.test
        TEST = True

    # exit(0)

    fan = PWMLED(GPIO_PIN)
    fan.on()
    fan_on = False
    fan.value = 0
    temp_seuil = (TEMP_MAX + TEMP_MIN) / 2

    while count > 0:
        if TEST:
            count += -1
        temp = get_temp()
        if not fan_on and temp > temp_seuil:
            fan_on = True
        if temp < TEMP_MIN:
            fan_on = False
            fan.value = 0
        if fan_on:
            voltage = get_voltage()
            fan.value = voltage
        if TEST:
            print(u'temp: {} voltage: {}'.format(temp, fan.value))
        time.sleep(SLEEP_INTERVAL)


if __name__ == '__main__':
    main()
