import numpy as np
import scipy.optimize

from structures.molecule_set import MoleculeSet


def run_one_iter(data, molecules: MoleculeSet, method):
    method.parameters.load_packed(data)
    results = {}
    for molecule in molecules:
        charges = method.calculate_charges(molecule)
        results[molecule.name] = charges


def parameterize(molecules, method):
    x0 = np.zeros(10, dtype=np.float32)
    scipy.optimize.minimize(run_one_iter, x0, args=(molecules, method))
