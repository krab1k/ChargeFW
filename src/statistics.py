from collections import namedtuple

import numpy as np

from charges import Charges
from structures.molecule_set import MoleculeSet


class Statistics(namedtuple('Statistics', 'rmsd pearson2 avg_diff max_diff')):
    __slots__ = ()

    def __repr__(self):
        return 'Statistics({0.rmsd:.2f}, {0.pearson2:.2f}, {0.avg_diff:.2f}, {0.max_diff:.2f})'.format(self)


def mean(x: np.ndarray):
    return x.sum() / len(x)


def corrcoef(x1: np.ndarray, x2: np.ndarray):
    x1m = x1 - mean(x1)
    x2m = x2 - mean(x2)
    return np.dot(x1m, x2m) ** 2 / (np.dot(x1m, x1m) * np.dot(x2m, x2m))


def calculate_all_total(ref_charges: Charges, charges: Charges) -> Statistics:
    np.seterr(divide='ignore', invalid='ignore')
    total_rmsd = 0
    total_pearson2 = 0
    total_avg_diff = 0
    total_max_diff = 0

    bad_molecules = 0
    for molecule_name in ref_charges:
        x1 = ref_charges[molecule_name]
        x2 = charges[molecule_name]
        if np.isnan(x2[0]) or np.isnan(x1[0]):
            bad_molecules += 1
            continue

        abs_diff = np.abs(x1 - x2)

        total_pearson2 += corrcoef(x1, x2)
        total_rmsd += (mean(abs_diff ** 2)) ** 0.5
        total_avg_diff += mean(abs_diff)
        total_max_diff += abs_diff.max()

    n = len(ref_charges) - bad_molecules + 1  # +1 to avoid zero if all molecules are bad

    return Statistics(total_rmsd / n, total_pearson2 / n, total_avg_diff / n, total_max_diff / n)


def calculate_all_per_atom_type(molecules: MoleculeSet, ref_charges: Charges, charges: Charges) -> dict:
    np.seterr(divide='ignore', invalid='ignore')
    results = dict()

    for atom_type in molecules.atom_types:
        indices = molecules.atom_types[atom_type]
        n = len(indices)
        x = np.empty(n, dtype=np.float32)
        y = np.empty(n, dtype=np.float32)

        for idx, ij in enumerate(indices):
            i, j = ij
            name = molecules[i].name
            x[idx] = ref_charges[name][j]
            y[idx] = charges[name][j]

        abs_diff = np.abs(x - y)
        rmsd = (mean(abs_diff ** 2)) ** 0.5
        pearson2 = corrcoef(x, y)
        avg_diff = mean(abs_diff)
        max_diff = abs_diff.max()

        results[atom_type] = Statistics(rmsd, pearson2, avg_diff, max_diff)

    return results


def calculate_statistics(molecules: MoleculeSet, ref_charges: Charges, charges: Charges):
    total_results = calculate_all_total(ref_charges, charges)
    per_atom_type_results = calculate_all_per_atom_type(molecules, ref_charges, charges)

    return total_results.rmsd
