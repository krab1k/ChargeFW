import argparse
import importlib
from collections import namedtuple

from charge_method import get_charge_methods
from classifier import classifiers

CommandLineOption = namedtuple('CommandLineOption', 'name help type default')


def parse_arguments():
    common_parser = argparse.ArgumentParser(add_help=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    common_parser.add_argument('--classifier', choices=classifiers.keys(), default='plain')
    common_parser.add_argument('-v', '--verbose', action='store_true', default=False)
    common_parser.add_argument('--debug', action='store_true', default=False)

    parser = argparse.ArgumentParser(description='ChargeFW', parents=[common_parser],
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(dest='command')

    info_parser = subparsers.add_parser('info', help='Print info about molecule set')
    info_parser.add_argument('sdf_file', help='SDF file')

    charges_parser = subparsers.add_parser('charges', help='Calculate charges')

    method_subparsers = charges_parser.add_subparsers(dest='method')
    for method in get_charge_methods():
        m = importlib.import_module('methods.' + method)
        method_parser = method_subparsers.add_parser(m.ChargeMethod.NAME,
                                                     description=m.ChargeMethod.FULL_NAME,
                                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        method_parser.add_argument('sdf_file', help='SDF file')
        method_parser.add_argument('charges_outfile', help='File for outputting charges')

        for option in m.ChargeMethod.OPTIONS:
            method_parser.add_argument('--' + option.name, dest='method_' + option.name, metavar=option.name.upper(),
                                       help=option.help, type=option.type, default=option.default)

    parameterization_parser = subparsers.add_parser('parameterize', help='Parameterize method')
    parameterization_parser.add_argument('method', choices=get_charge_methods(), help='Charge calculation method')

    args = parser.parse_args()

    if args.debug:
        print(args)

    global_options = {}
    method_options = {}
    for arg in vars(args):
        if arg.startswith('method_'):
            method_options[arg[len("method_"):]] = getattr(args, arg)
        else:
            global_options[arg] = getattr(args, arg)

    return global_options, method_options
