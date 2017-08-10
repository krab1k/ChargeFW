import operator
from copy import deepcopy

import numpy as np
import scipy.optimize

from charge_method import ChargeMethodSkeleton
from charges import Charges
from statistics import calculate_statistics
from structures.molecule_set import MoleculeSet


def run_one_iter(data: np.ndarray, molecules: MoleculeSet, method: ChargeMethodSkeleton, ref_charges: Charges):
    method.parameters.load_packed(data)
    results = {}
    for molecule in molecules:
        results[molecule.name] = method.calculate_charges(molecule)

    new_charges: Charges = Charges(results)
    rmsd = calculate_statistics(molecules, ref_charges, new_charges)
    return rmsd


def one_process(molecules: MoleculeSet, method: ChargeMethodSkeleton, ref_charges: Charges):
    method.parameters.set_random_values()
    method.parameters.print_parameters()
    x0 = method.parameters.pack_values()
    return scipy.optimize.minimize(run_one_iter, x0, args=(molecules, method, ref_charges), method='L-BFGS-B',
                                   options={'maxiter': 10})


def parameterize(molecules: MoleculeSet, method: ChargeMethodSkeleton, ref_charges: Charges):
    population_size = 1
    population = [deepcopy(method) for _ in range(population_size)]

    results = []
    for m in population:
        results.append(one_process(molecules, m, ref_charges))

    results = [result.fun for result in results]
    index, value = min(enumerate(results), key=operator.itemgetter(1))

    method.parameters.load_packed(population[index].parameters.pack_values())
