#!/usr/bin/env python3
import argparse
import importlib
import pkgutil

from charges import Charges
from classifier import classifiers
from structures.molecule_set import MoleculeSet


def get_charge_methods():
    return list(module.name for module in pkgutil.iter_modules(['methods']))


def main():
    parser = argparse.ArgumentParser(description='ChargeFW')
    subparsers = parser.add_subparsers(dest='command')

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument('sdf_file', help='SDF file')
    common_parser.add_argument('--classifier', choices=classifiers.keys(), default='plain')
    common_parser.add_argument('-v', '--verbose', action='store_true')
    common_parser.add_argument('--debug', action='store_true')

    # noinspection PyUnusedLocal
    info_parser = subparsers.add_parser('info', help='Print info about molecule set', parents=[common_parser])

    charges_parser = subparsers.add_parser('charges', help='Calculate charges', parents=[common_parser])
    charges_parser.add_argument('method', choices=get_charge_methods(), help='Charge calculation method')
    charges_parser.add_argument('charges_outfile', help='File for outputting charges')

    parameterization_parser = subparsers.add_parser('parameterize', help='Parameterize method', parents=[common_parser])
    parameterization_parser.add_argument('method', choices=get_charge_methods(), help='Charge calculation method')

    args = parser.parse_args()

    if args.debug:
        print(args)

    if args.command == 'info':
        molecules = MoleculeSet.load_from_file(args.sdf_file)
        molecules.stats(classifiers[args.classifier])

    elif args.command == 'charges':
        molecules = MoleculeSet.load_from_file(args.sdf_file)

        module = importlib.import_module('methods.' + args.method)
        method = module.ChargeMethod()
        method.initialize()

        charges = Charges()
        for molecule in molecules:
            charges[molecule.name] = method.calculate_charges(molecule)

        charges.save_to_file(args.charges_outfile)


if __name__ == '__main__':
    main()
