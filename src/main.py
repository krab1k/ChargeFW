#!/usr/bin/env python3

import importlib

from charges import Charges
from classifier import classifiers, ParametersClassifier
from options import parse_arguments
from structures.molecule_set import MoleculeSet


def main():
    global_options, method_options = parse_arguments()

    if global_options['command'] == 'info':
        molecules = MoleculeSet.load_from_file(global_options['sdf_file'])
        molecules.assign_atom_types(classifiers[global_options['classifier']])
        molecules.stats()

    elif global_options['command'] == 'charges':
        molecules = MoleculeSet.load_from_file(global_options['sdf_file'])

        m = importlib.import_module('methods.' + global_options['method'])
        method = m.ChargeMethod()
        method.initialize(method_options)

        pc = ParametersClassifier(method.parameters.atom)
        molecules.assign_atom_types(pc)

        charges = Charges()
        for molecule in molecules:
            charges[molecule.name] = method.calculate_charges(molecule)

        charges.save_to_file(global_options['charges_outfile'])


if __name__ == '__main__':
    main()
