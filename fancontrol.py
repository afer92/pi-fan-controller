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


def get_temp() -> float:
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


def get_voltage(params: dict) -> float:
    """ Compute voltage from cpu temp and parameters.
    Parameters:
        params: dict
            User parameters for fan control
    Returns:
        float: 0.0 to 1.0
    """
    delta_t = params['temp_max'] - params['temp_min']  # delta consigne
    delta_v = params['percent_high'] - params['percent_low']
    step = delta_v / delta_t
    computed_v = get_temp() - params['temp_min']
    if computed_v <= 0:
        return 0
    computed_v = params['percent_low'] + (computed_v * step)
    if computed_v > 1:
        return 1
    return computed_v


def print_infos(params: dict):
    """ Dump parameters, temperature and computed voltage
    Parameters:
        params: dict
            User parameters for fan control
    Returns:
        None
    """
    print(u'gpio_pin : \t{}'.format(params['gpio_pin']))
    print(u'SLEEP : \t{}s'.format(params['sleep_interval']))
    print(u'temp_min : \t{}°C'.format(params['temp_min']))
    print(u'temp_max : \t{}°C'.format(params['temp_max']))
    print(u'percent_low : \t{}% ({}V)'.format(params['percent_low'],
                                              params['percent_low']*5))
    print(u'percent_high : \t{}% ({}V)'.format(params['percent_high'],
                                               params['percent_high']*5))
    print(u'CPU_TEMP : \t{}°C'.format(get_temp()))
    percent = get_voltage(params)
    print(u'VOLTAGE : \t{:.2f}% ({:.2f}V)'.format(percent, percent*5))


def get_args():
    """ Parse args from command line """

    # Default parameter values

    temp_min = 40  # Temperature (or lower) where fan voltage is 0.0
    temp_max = 50  # Temperature (or higher) where van voltage is 1.0
    sleep_interval = 5  # (seconds) How often we check the core temperature.
    gpio_pin = 17  # Which GPIO pin you're using to control the fan.
    percent_high = 0.6
    percent_low = 0.4
    test = False

    parseFormatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=parseFormatter)
    parser.add_argument("-i", "--infos",
                        help="print parameters, tempcpu and voltage",
                        action="store_true")
    parser.add_argument("-v", "--verbose",
                        help="verbose",
                        action="store_true")
    parser.add_argument("-V", "--version",
                        help="program version",
                        action="store_true")
    parser.add_argument("-m", "--temp_min",
                        help="temp_min °C", type=int, default=temp_min)
    parser.add_argument("-M", "--temp_max",
                        help="temp_max °C", type=int, default=temp_max)
    parser.add_argument("-p", "--percent_low",
                        help="percent_low %%", type=float, default=percent_low)
    parser.add_argument("-P", "--percent_high",
                        help="percent_high %%", type=float,
                        default=percent_high)
    parser.add_argument("-G", "--gpio_pin", default=gpio_pin,
                        help="gpio_pin", type=int)
    parser.add_argument("-t", "--test",
                        help="""run test cycles and
                                display temperature and voltage""",
                        type=int, default=test)
    parser.add_argument("-s", "--sleep_interval",
                        type=int, help="sleep_interval seconds",
                        default=sleep_interval)
    return parser.parse_args()


def load_params(args) -> dict:
    """ Load params with default value and line command args

    Returns:
        params as a dictionnary
    """

    # Validate
    if args.temp_min >= args.temp_max:
        raise RuntimeError('temp_min must be less than temp_max')

    # Load params
    params = {
              'temp_min': args.temp_min,
              'temp_max': args.temp_max,
              'percent_low': args.percent_low,
              'percent_high': args.percent_high,
              'test': args.test,
              'sleep_interval': args.sleep_interval,
              'gpio_pin': args.gpio_pin,
              }
    return params


def main():
    """ Main loop """

    args = get_args()
    params = load_params(args)
    test = False

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
