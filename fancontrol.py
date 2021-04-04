#!/usr/bin/env python3
""" Raspberry Pi fan controller """
import argparse
import subprocess
import time
import sys

from gpiozero.pins.rpigpio import RPiGPIOFactory
from gpiozero import PWMLED


PI_FAN_CONTROLLER_VERSION = "1.0.0"

__author__ = "Alain Ferraro (aka afer92)"
__copyright__ = "Copyright 2021, Alain Ferraro"
__credits__ = ["Dave Fletcher", "howchoo"]
__license__ = "GPL"
__version__ = PI_FAN_CONTROLLER_VERSION
__maintainer__ = "afer92"
__email__ = ""
__status__ = "Production"


def get_temp():
    """Get the core temperature.

    Run a shell script to get the core temp and parse the output.

    Raises:
        RuntimeError: if response cannot be parsed.

    Returns:
        float: The core temperature in degrees Celsius.
    """
    output = subprocess.run(['vcgencmd', 'measure_temp'],
                            check=True, capture_output=True)
    temp_str = output.stdout.decode()
    try:
        return float(temp_str.split('=')[1].split('\'')[0])
    except (IndexError, ValueError) as parse_temp_output:
        raise RuntimeError('Could not parse temperature output.')\
              from parse_temp_output


def get_voltage(params):
    """ Compute voltage from cpu temp and parameters """
    delta_t = params['temp_max'] - params['temp_min']  # delta consigne
    delta_v = params['high_percent'] - params['low_percent']
    step = delta_v / delta_t
    computed_v = get_temp() - params['temp_min']
    if computed_v <= 0:
        return 0
    computed_v = params['low_percent'] + (computed_v * step)
    if computed_v > 1:
        return 1
    return computed_v


def print_infos(params):
    """ Dump parameters, temperature and computed voltage """
    print(u'gpio_pin : \t{}'.format(params['gpio_pin']))
    print(u'SLEEP : \t{}s'.format(params['sleep_interval']))
    print(u'temp_min : \t{}°C'.format(params['temp_min']))
    print(u'temp_max : \t{}°C'.format(params['temp_max']))
    print(u'low_percent : \t{}% ({}V)'.format(params['low_percent'],
                                              params['low_percent']*5))
    print(u'high_percent : \t{}% ({}V)'.format(params['high_percent'],
                                               params['high_percent']*5))
    print(u'CPU_TEMP : \t{}°C'.format(get_temp()))
    percent = get_voltage(params)
    print(u'VOLTAGE : \t{:.2f}% ({:.2f}V)'.format(percent, percent*5))


def get_args():
    """ Parse args from command line """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infos",
                        help="print parameters, tempcpu and voltage",
                        action="store_true")
    parser.add_argument("-v", "--verbose",
                        help="verbose",
                        action="store_true")
    parser.add_argument("-V", "--version",
                        help="verbose",
                        action="store_true")
    parser.add_argument("-m", "--temp_min",
                        help="temp_min", type=int)
    parser.add_argument("-M", "--temp_max",
                        help="temp_max", type=int)
    parser.add_argument("-p", "--percent_low",
                        help="low_percent", type=float)
    parser.add_argument("-P", "--percent_high",
                        help="high_percent", type=float)
    parser.add_argument("-G", "--gpio_pin",
                        help="temp_max", type=int)
    parser.add_argument("-t", "--test",
                        help="""run test cycles and
                                display temperature and voltage""", type=int)
    return parser.parse_args()


def load_params(args):
    """ Load params with default value and line command args """

    # Default parameter values

    temp_min = 40  # Temperature (or lower) where fan voltage is 0.0
    temp_max = 50  # Temperature (or higher) where van voltage is 1.0
    sleep_interval = 5  # (seconds) How often we check the core temperature.
    gpio_pin = 17  # Which GPIO pin you're using to control the fan.
    high_percent = 0.6
    low_percent = 0.4
    test = False

    if args.temp_min:
        temp_min = args.temp_min
    if args.temp_max:
        temp_max = args.temp_max
    if args.percent_low:
        low_percent = args.percent_low
    if args.percent_high:
        high_percent = args.percent_high
    if args.gpio_pin:
        gpio_pin = args.gpio_pin

    # Validate
    if temp_min >= temp_max:
        raise RuntimeError('temp_min must be less than temp_max')

    # Load params
    params = {
              'temp_min': temp_min,
              'temp_max': temp_max,
              'low_percent': low_percent,
              'high_percent': high_percent,
              'test': test,
              'sleep_interval': sleep_interval,
              'gpio_pin': gpio_pin,
              }
    return params


def main():
    """ Main loop """

    args = get_args()
    params = load_params(args)

    if args.version:
        print(u'Version : {}'.format(__version__))
        sys.exit(0)

    if args.infos:
        print_infos(params)
        sys.exit(0)

    if args.verbose:
        print_infos(params)

    count = 1
    if args.test:
        count = args.test
        test = True

    # exit(0)

    factory = RPiGPIOFactory()
    fan = PWMLED(params['gpio_pin'], pin_factory=factory)
    fan.on()
    fan_on = False
    fan.value = 0
    temp_seuil = (params['temp_max'] + params['temp_min']) / 2

    while count > 0:
        if test:
            count += -1
        temp = get_temp()
        if not fan_on and temp > temp_seuil:
            fan_on = True
        if temp < params['temp_min']:
            fan_on = False
            fan.value = 0
        if fan_on:
            voltage = get_voltage(params)
            fan.value = voltage
        if test:
            print(u'temp: {} voltage: {}'.format(temp, fan.value), flush=True)
        time.sleep(params['sleep_interval'])


if __name__ == '__main__':
    main()
