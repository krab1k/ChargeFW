#!/usr/bin/env python3

import importlib
from pprint import pprint

from charges import Charges
from classifier import classifiers, ParametersClassifier
from options import parse_arguments
from parameterization import parameterize
from statistics import calculate_all_total, calculate_all_per_atom_type
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

        charges: Charges = Charges()
        for molecule in molecules:
            charges[molecule.name] = method.calculate_charges(molecule)

        charges.save_to_file(global_options['charges_outfile'])

    elif global_options['command'] == 'parameters':
        molecules = MoleculeSet.load_from_file(global_options['sdf_file'])
        molecules.assign_atom_types(classifiers[global_options['classifier']])
        m = importlib.import_module('methods.' + global_options['method'])

        ref_charges = Charges.load_from_file(global_options['charge_file'])
        method = m.ChargeMethod()
        method.parameters.init_from_set(molecules)
        method.parameters.set_ranges({'kappa': (0.0, 1)}, {'A': (1.6, 3.2), 'B': (0, 1.8)})
        parameterize(molecules, method, ref_charges)

        new_charges: Charges = Charges()
        for molecule in molecules:
            new_charges[molecule.name] = method.calculate_charges(molecule)

        pprint(calculate_all_total(ref_charges, new_charges))
        pprint(calculate_all_per_atom_type(molecules, ref_charges, new_charges))


if __name__ == '__main__':
    main()
