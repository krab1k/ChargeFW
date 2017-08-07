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

    new_charges = Charges(results)
    rmsd = calculate_statistics(molecules, ref_charges, new_charges)
    return rmsd


def parameterize(molecules: MoleculeSet, method: ChargeMethodSkeleton, ref_charges: Charges):
    n = len(method.COMMON_PARAMETERS) + len(method.ATOM_PARAMETERS) * len(molecules.atom_types)
    x0 = np.ones(n, dtype=np.float32)
    # minimizer_kwargs = {'method': 'L-BFGS-B', 'args': (molecules, method, ref_charges)}
    # res = scipy.optimize.basinhopping(run_one_iter, x0, minimizer_kwargs=minimizer_kwargs)
    scipy.optimize.minimize(run_one_iter, x0, args=(molecules, method, ref_charges))
