from collections import namedtuple
from typing import Tuple

import numpy as np

from charges import Charges
from structures.molecule_set import MoleculeSet

statistics = namedtuple('Statistics', 'rmsd pearson2 avg_diff max_diff')


def calculate_all_total(ref_charges: Charges, charges: Charges) -> Tuple[float, float, float, float]:
    total_rmsd = 0
    total_pearson2 = 0
    total_avg_diff = 0
    total_max_diff = 0

    for molecule_name in ref_charges:
        x1 = ref_charges[molecule_name]
        x2 = charges[molecule_name]
        abs_diff = np.abs(x1 - x2)

        total_rmsd += np.sqrt(np.mean(np.square(abs_diff)))
        total_pearson2 += np.corrcoef(x1, x2)[1, 0] ** 2
        total_avg_diff += np.mean(abs_diff)
        total_max_diff += np.max(abs_diff)

    n = len(ref_charges)

    return total_rmsd / n, total_pearson2 / n, total_avg_diff / n, total_max_diff / n


def calculate_all_per_atom_type(molecules: MoleculeSet, ref_charges: Charges, charges: Charges) -> dict:
    results = dict()

    for atom_type in molecules.atom_types:
        indices = molecules.atom_types[atom_type]
        n = len(indices)
        x = np.empty(n, dtype=np.float32)
        y = np.empty(n, dtype=np.float32)

        for idx, i, j in enumerate(indices):
            name = molecules[i].name
            x[idx] = ref_charges[name][j]
            y[idx] = charges[name][j]

        abs_diff = np.abs(x - y)
        rmsd = np.sqrt(np.mean(np.square(abs_diff)))
        pearson2 = np.corrcoef(x, y)[1, 0] ** 2
        avg_diff = np.mean(abs_diff)
        max_diff = np.max(abs_diff)

        results[atom_type] = rmsd, pearson2, avg_diff, max_diff

    return results


def calculate_statistics(molecules: MoleculeSet, ref_charges: Charges, charges: Charges):
    rmsd, pearson2, avg_diff, max_diff = calculate_all_total(ref_charges, charges)
    per_atom_type_results = calculate_all_per_atom_type(molecules, ref_charges, charges)

    return rmsd
